import random
from typing import List, Literal, Optional, TypeVar

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

    def match(self, query: str, role: Role, num: int = 1) -> List[Profile]:
        self._initialize_retriever()

        profiles = self.get(**{f'is_{role}_candidate': True})
        query_embed = get_embed([query], self.retriever_tokenizer, self.retriever_model)

        corpus_embed = []
        for profile in profiles:
            if profile.pk in self.data_embed:
                corpus_embed.append(self.data_embed[profile.pk])
            else:
                profile_embed = get_embed(
                    instructions=[profile.bio],
                    retriever_tokenizer=self.retriever_tokenizer,
                    retriever_model=self.retriever_model,
                )[0]
                corpus_embed.append(profile_embed)

        topk_indexes = rank_topk(query_embed, corpus_embed, num=num)
        matched_profiles = [profiles[idx] for topk in topk_indexes for idx in topk]

        logger.info(f'Matched profiles for role {role}: {matched_profiles}')
        return matched_profiles

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
