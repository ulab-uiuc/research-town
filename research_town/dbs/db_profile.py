import random
from typing import Any, List, Optional, TypeVar, get_type_hints

from transformers import BertModel, BertTokenizer

from ..configs import Config
from ..utils.logger import logger
from ..utils.profile_collector import (
    collect_publications_and_coauthors,
    summarize_domain_prompting,
    write_bio_prompting,
)
from ..utils.retriever import get_embed, rank_topk
from .data import Data, Profile, Proposal
from .db_base import BaseDB

T = TypeVar('T', bound=Data)


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
            publication_info = '; '.join(publications)

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

    def match(self, query: str, num: int = 1, **conditions: Any) -> List[Profile]:
        self._initialize_retriever()

        profiles = self.get(**conditions)
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

        logger.info(f'Matched profiles: {matched_profiles}')
        return matched_profiles

    def sample(self, num: int = 1, **conditions: Any) -> List[Profile]:
        profiles = self.get(**conditions)
        random.shuffle(profiles)
        return profiles[:num]

    def transform_to_embed(self) -> None:
        self._initialize_retriever()
        for pk, profile in self.data.items():
            self.data_embed[pk] = get_embed(
                [profile.bio], self.retriever_tokenizer, self.retriever_model
            )[0]

    def reset_role_availability(self) -> None:
        for profile in self.data.values():
            profile.update_roles(
                is_leader=True, is_member=True, is_reviewer=True, is_chair=True
            )
            self.update(pk=profile.pk, updates=profile.model_dump())

    def _update_profile_roles(self, profiles: List[Profile], role_field: str) -> None:
        role_fields = [
            field
            for field, field_type in get_type_hints(Profile).items()
            if field.startswith('is_') and isinstance(field_type, bool)
        ]

        for profile in profiles:
            for field in role_fields:
                setattr(profile, field, False)
            setattr(profile, role_field, True)
            self.update(pk=profile.pk, updates=profile.model_dump())

    def match_profiles_by_role(
        self, query: str, role: str, num: int = 1
    ) -> List[Profile]:
        return self.match(query=query, num=num, **{f'is_{role}_candidate': True})

    def sample_profiles_by_role(self, role: str, num: int = 1) -> List[Profile]:
        profiles = self.sample(num=num, **{f'is_{role}_candidate': True})
        self._update_profile_roles(profiles, f'is_{role}_candidate')
        return profiles

    # Specific role matching functions
    def match_member_profiles(
        self, leader: Profile, member_num: int = 1
    ) -> List[Profile]:
        return self.match_profiles_by_role(leader.bio, 'member', member_num)

    def match_reviewer_profiles(
        self, proposal: Proposal, reviewer_num: int = 1
    ) -> List[Profile]:
        return self.match_profiles_by_role(proposal.content, 'reviewer', reviewer_num)

    def match_chair_profiles(
        self, proposal: Proposal, chair_num: int = 1
    ) -> List[Profile]:
        return self.match_profiles_by_role(proposal.content, 'chair', chair_num)

    def match_leader_profiles(self, query: str, leader_num: int = 1) -> List[Profile]:
        return self.match_profiles_by_role(query, 'leader', leader_num)

    # Specific role sampling functions
    def sample_leader_profiles(self, leader_num: int = 1) -> List[Profile]:
        return self.sample_profiles_by_role('leader', leader_num)

    def sample_chair_profiles(self, chair_num: int = 1) -> List[Profile]:
        return self.sample_profiles_by_role('chair', chair_num)

    def sample_member_profiles(self, member_num: int = 1) -> List[Profile]:
        return self.sample_profiles_by_role('member', member_num)

    def sample_reviewer_profiles(self, reviewer_num: int = 1) -> List[Profile]:
        return self.sample_profiles_by_role('reviewer', reviewer_num)

    def sample_leader_profile(self) -> Profile:
        return self.sample_leader_profiles(1)[0]
