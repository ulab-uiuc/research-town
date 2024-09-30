import random
from typing import List, Literal, Optional, TypeVar

import requests
from transformers import BertModel, BertTokenizer

from ..configs import Config
from ..data.data import Data, Profile
from ..utils.logger import logger
from ..utils.profile_collector import (
    collect_publications_and_coauthors,
    summarize_domain_prompting,
    write_bio_prompting,
)
from ..utils.retriever import get_embed, rank_topk
from .db_base import BaseDB

T = TypeVar('T', bound=Data)

Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class ProfileDB(BaseDB[Profile]):
    SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/author/search'

    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(Profile, load_file_path)
        self.retriever_tokenizer: Optional[BertTokenizer] = None
        self.retriever_model: Optional[BertModel] = None

    def _initialize_retriever(self) -> None:
        if not self.retriever_tokenizer or not self.retriever_model:
            self.retriever_tokenizer = BertTokenizer.from_pretrained(
                'facebook/contriever'
            )
            self.retriever_model = BertModel.from_pretrained('facebook/contriever')

    def pull_profiles(self, names: List[str], config: Config) -> None:
        for name in names:
            publications, collaborators = collect_publications_and_coauthors(
                name, paper_max_num=20
            )
            publication_info = '; '.join([f'{abstract}' for abstract in publications])

            bio = write_bio_prompting(
                publication_info=publication_info,
                prompt_template=config.agent_prompt_template.write_bio,
                model_name=config.param.base_llm,
            )
            domain = summarize_domain_prompting(
                publication_info=publication_info,
                prompt_template=config.agent_prompt_template.summarize_domain,
                model_name=config.param.base_llm,
            )

            profile = Profile(
                name=name, bio=bio, domain=domain, collaborators=collaborators
            )
            self.add(profile)
        self.transform_to_embed()

    def transform_to_embed(self) -> None:
        self._initialize_retriever()
        for pk, profile in self.data.items():
            self.data_embed[pk] = get_embed(
                [profile.bio], self.retriever_tokenizer, self.retriever_model
            )[0]

    def match_offline(
        self, query: str, role: Optional[Role], num: int = 1
    ) -> List[Profile]:
        self._initialize_retriever()

        profiles = self.get(**{f'is_{role}_candidate': True})
        query_embed = get_embed([query], self.retriever_tokenizer, self.retriever_model)

        corpus_embed = [
            self.data_embed.get(profile.pk)
            or get_embed([profile.bio], self.retriever_tokenizer, self.retriever_model)[
                0
            ]
            for profile in profiles
        ]

        topk_indexes = rank_topk(query_embed, corpus_embed, num=num)
        matched_profiles = [profiles[idx] for topk in topk_indexes for idx in topk]

        logger.info(f'Matched profiles for role {role}: {matched_profiles}')
        return matched_profiles

    def match_online(
        self,
        query: Optional[str] = None,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        num: int = 1,
    ) -> List[Profile]:
        if not query and not name:
            logger.warning('No query or name provided for online matching.')
            return []

        search_query = query if query else name
        params = {
            'query': search_query,
            'fields': 'name,publications,affiliations',
            'limit': num,
        }

        try:
            response = requests.get(self.SEMANTIC_SCHOLAR_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            logger.debug('Received response from Semantic Scholar API.')
        except requests.exceptions.RequestException as e:
            logger.error(f'Semantic Scholar API request failed: {e}')
            return []

        matched_profiles = []
        for author in data.get('data', []):
            if domain:
                papers = author.get('publications', [])
                if not any(
                    domain.lower() in paper.get('title', '').lower()
                    or domain.lower() in paper.get('abstract', '').lower()
                    for paper in papers
                ):
                    continue

            try:
                affiliations = [
                    aff.get('name', '') for aff in author.get('affiliations', [])
                ]
                bio = (
                    f"Affiliations: {', '.join(affiliations)}"
                    if affiliations
                    else 'No affiliations listed.'
                )

                profile = Profile(
                    name=author.get('name', 'Unknown'),
                    bio=bio,
                    domain=domain or 'Unknown',
                    collaborators=[],
                )
                matched_profiles.append(profile)
            except Exception as e:
                logger.error(
                    f'Failed to construct or add profile from online data: {e}'
                )
                continue

            if len(matched_profiles) >= num:
                break

        logger.info(f'Matched profiles (online): {matched_profiles}')
        return matched_profiles

    def match(
        self,
        query: Optional[str] = None,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        role: Optional[Role] = None,
        num: int = 1,
    ) -> List[Profile]:
        if query:
            offline_results = self.match_offline(query=query, role=role, num=num)
        elif name:
            offline_results = self.match_offline(query=name, role=role, num=num)
        else:
            offline_results = []

        if len(offline_results) >= num:
            return offline_results[:num]

        remaining = num - len(offline_results)
        online_results = self.match_online(
            query=query, name=name, domain=domain, num=remaining
        )

        combined_results = offline_results + online_results
        return combined_results[:num]

    def sample(self, role: Role, num: int = 1) -> List[Profile]:
        profiles = self.get(**{f'is_{role}_candidate': True})
        random.shuffle(profiles)
        sampled_profiles = profiles[:num]
        return sampled_profiles

    def reset_role_availability(self) -> None:
        for profile in self.data.values():
            profile.is_leader_candidate = True
            profile.is_member_candidate = True
            profile.is_reviewer_candidate = True
            profile.is_chair_candidate = True
            self.update(pk=profile.pk, updates=profile.model_dump())
