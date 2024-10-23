import random
from typing import List, Literal, Optional, TypeVar

from transformers import BertModel, BertTokenizer

from ..configs import Config, DatabaseConfig
from ..data.data import Data, Profile
from ..utils.logger import logger
from ..utils.profile_collector import (
    collect_publications_and_coauthors,
    summarize_domain_prompting,
    write_bio_prompting,
)
from ..utils.retriever import get_embed
from .db_base import BaseDB

T = TypeVar('T', bound=Data)

Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class ProfileDB(BaseDB[Profile]):
    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__(Profile, config=config, with_embeddings=True)
        self.retriever_tokenizer: Optional[BertTokenizer] = None
        self.retriever_model: Optional[BertModel] = None

    def _initialize_retriever(self) -> None:
        if not self.retriever_tokenizer or not self.retriever_model:
            self.retriever_tokenizer = BertTokenizer.from_pretrained(
                'facebook/contriever'
            )
            self.retriever_model = BertModel.from_pretrained('facebook/contriever')

    def pull_profiles(
        self,
        names: List[str],
        config: Config,
        exclude_paper_titles: Optional[List[str]] = None,
    ) -> None:
        if exclude_paper_titles is None:
            exclude_paper_titles = ['']
        profiles: List[Profile] = []
        for name in names:
            pub_abstracts, pub_titles, collaborators = (
                collect_publications_and_coauthors(
                    name, paper_max_num=20, exclude_paper_titles=exclude_paper_titles
                )
            )
            pub_info = '; '.join([f'{abstract}' for abstract in pub_abstracts])

            bio = write_bio_prompting(
                pub_info=pub_info,
                prompt_template=config.agent_prompt_template.write_bio,
                model_name=config.param.base_llm,
            )
            domain = summarize_domain_prompting(
                pub_info=pub_info,
                prompt_template=config.agent_prompt_template.summarize_domain,
                model_name=config.param.base_llm,
            )

            profile = Profile(
                name=name,
                bio=bio,
                domain=domain,
                collaborators=collaborators,
                pub_titles=pub_titles,
                pub_abstracts=pub_abstracts,
            )
            profiles.append(profile)
        self._initialize_retriever()
        embeddings = get_embed(
            [profile.bio for profile in profiles],
            self.retriever_tokenizer,
            self.retriever_model,
        )
        for profile, emb in zip(profiles, embeddings):
            profile.embed = emb
            self.add(profile)

    def match(self, query: str, role: Role, num: int = 1) -> List[Profile]:
        self._initialize_retriever()

        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        query_embeddings = [t.numpy(force=True).squeeze() for t in query_embed]

        match_profile_data = self.database_client.search(
            self.data_class.__name__,
            query_embeddings,
            num=num,
            **{f'is_{role}_candidate': True},
        )[0]
        matched_profiles = [self.data_class(**d) for d in match_profile_data]

        logger.info(f'Matched profiles for role {role}: {matched_profiles}')
        return matched_profiles

    def sample(self, role: Role, num: int = 1) -> List[Profile]:
        profiles = self.get(**{f'is_{role}_candidate': True})
        random.shuffle(profiles)
        sampled_profiles = profiles[:num]
        return sampled_profiles

    def reset_role_availability(self) -> None:
        profiles = self.get()
        for profile in profiles:
            profile.is_leader_candidate = True
            profile.is_member_candidate = True
            profile.is_reviewer_candidate = True
            profile.is_chair_candidate = True
            self.update(pk=profile.pk, updates=profile.model_dump())

    def add(self, data: Profile) -> None:
        self._initialize_retriever()
        if data.embed is None:
            data.embed = get_embed(
                [data.bio], self.retriever_tokenizer, self.retriever_model
            )[0]
        super().add(data)
