from typing import Any, Dict, List, Optional, TypeVar

from transformers import BertModel, BertTokenizer

from ..configs import Config
from ..utils.agent_collector import collect_proposals_and_coauthors
from ..utils.agent_prompter import write_bio_prompting
from ..utils.logger import logger
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
        if self.retriever_tokenizer is None or self.retriever_model is None:
            self.retriever_tokenizer = BertTokenizer.from_pretrained(
                'facebook/contriever'
            )
            self.retriever_model = BertModel.from_pretrained('facebook/contriever')

    def pull_profiles(self, agent_names: List[str], config: Config) -> None:
        for name in agent_names:
            proposals, collaborators = collect_proposals_and_coauthors(
                author=name, paper_max_num=10
            )
            publication_info = '; '.join([f'{abstract}' for abstract in proposals])
            bio = write_bio_prompting(
                publication_info=publication_info,
                prompt_template=config.agent_prompt_template.write_bio,
            )[0]
            profile = Profile(
                name=name,
                bio=bio,
                collaborators=collaborators,
            )
            self.add(profile)

    def match(
        self,
        query: str,
        num: int = 1,
        updates: Optional[Dict[str, bool]] = None,
        **conditions: Dict[str, Any],
    ) -> List[Profile]:
        self._initialize_retriever()

        # Get agent profiles based on the provided conditions
        profiles = self.get(**conditions)

        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )

        corpus_embed = []
        for profile in profiles:
            if profile.pk in self.data_embed:
                corpus_embed.append(self.data_embed[profile.pk])
            else:
                agent_embed = get_embed(
                    instructions=[profile.bio],
                    retriever_tokenizer=self.retriever_tokenizer,
                    retriever_model=self.retriever_model,
                )[0]
                corpus_embed.append(agent_embed)

        topk_indexes = rank_topk(
            query_embed=query_embed, corpus_embed=corpus_embed, num=num
        )
        indexes = [index for topk_index in topk_indexes for index in topk_index]
        matched_profiles = [profiles[index] for index in indexes]

        # Apply updates to the matched profiles if updates are provided
        if updates:
            for agent in matched_profiles:
                for field, value in updates.items():
                    setattr(agent, field, value)
                self.update(pk=agent.pk, updates=agent.model_dump())

        logger.info(f'Matched agents: {matched_profiles}')
        return matched_profiles

    def transform_to_embed(self) -> None:
        self._initialize_retriever()
        for agent_pk in self.data:
            self.data_embed[agent_pk] = get_embed(
                [self.data[agent_pk].bio],
                self.retriever_tokenizer,
                self.retriever_model,
            )[0]

    def reset_role_availability(self) -> None:
        for profile in self.data.values():
            profile.is_leader_candidate = True
            profile.is_member_candidate = True
            profile.is_reviewer_candidate = True
            profile.is_chair_candidate = True
            self.update(pk=profile.pk, updates=profile.model_dump())

    def match_member_profiles(
        self, leader: Profile, member_num: int = 1
    ) -> List[Profile]:
        members = self.match(
            query=leader.bio,
            num=member_num,
            updates={
                'is_leader_candidate': False,
                'is_member_candidate': True,
                'is_reviewer_candidate': False,
                'is_chair_candidate': False,
            },
            is_member_candidate=True,
        )
        return members

    def match_reviewer_profiles(
        self, proposal: Proposal, reviewer_num: int = 1
    ) -> List[Profile]:
        reviewers = self.match(
            query=proposal.content if proposal.content else '',
            num=reviewer_num,
            updates={
                'is_leader_candidate': False,
                'is_member_candidate': False,
                'is_reviewer_candidate': True,
                'is_chair_candidate': False,
            },
            is_reviewer_candidate=True,
        )
        return reviewers

    def match_chair_profiles(
        self, proposal: Proposal, chair_num: int = 1
    ) -> List[Profile]:
        chairs = self.match(
            query=proposal.content,
            num=chair_num,
            updates={
                'is_leader_candidate': False,
                'is_member_candidate': False,
                'is_reviewer_candidate': False,
                'is_chair_candidate': True,
            },
            is_chair_candidate=True,
        )
        return chairs

    def match_leader_profiles(self, query: str, leader_num: int = 1) -> List[Profile]:
        leaders = self.match(
            query=query,
            num=leader_num,
            updates={
                'is_leader_candidate': True,
                'is_member_candidate': False,
                'is_reviewer_candidate': False,
                'is_chair_candidate': False,
            },
            is_leader_candidate=True,
        )
        return leaders
