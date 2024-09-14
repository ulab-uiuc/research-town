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
        self.retriever_tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
            'facebook/contriever'
        )
        self.retriever_model: BertModel = BertModel.from_pretrained(
            'facebook/contriever'
        )

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
            agent_profile = Profile(
                name=name,
                bio=bio,
                collaborators=collaborators,
            )
            self.add(agent_profile)

    def match(
        self, query: str, agent_profiles: List[Profile], num: int = 1
    ) -> List[Profile]:
        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )

        corpus_embed = []
        for agent_profile in agent_profiles:
            if agent_profile.pk in self.data_embed:
                corpus_embed.append(self.data_embed[agent_profile.pk])
            else:
                agent_embed = get_embed(
                    instructions=[agent_profile.bio],
                    retriever_tokenizer=self.retriever_tokenizer,
                    retriever_model=self.retriever_model,
                )[0]
                corpus_embed.append(agent_embed)
        topk_indexes = rank_topk(
            query_embed=query_embed, corpus_embed=corpus_embed, num=num
        )
        indexes = [index for topk_index in topk_indexes for index in topk_index]
        match_agent_profiles = [agent_profiles[index] for index in indexes]
        logger.info(f'Matched agents: {match_agent_profiles}')
        return match_agent_profiles

    def transform_to_embed(self) -> None:
        for agent_pk in self.data:
            self.data_embed[agent_pk] = get_embed(
                [self.data[agent_pk].bio],
                self.retriever_tokenizer,
                self.retriever_model,
            )[0]

    def reset_role_avaialbility(self) -> None:
        for profile in self.data.values():
            profile.is_leader_candidate = True
            profile.is_member_candidate = True
            profile.is_reviewer_candidate = True
            profile.is_chair_candidate = True
            self.update(pk=profile.pk, updates=profile.model_dump())

    def search_profiles(
        self,
        condition: Dict[str, Any],
        query: str,
        num: int,
        update_fields: Dict[str, bool],
    ) -> List[Profile]:
        candidates = self.get(**condition)
        searched_profiles = self.match(query=query, agent_profiles=candidates, num=num)

        for agent in searched_profiles:
            for field, value in update_fields.items():
                setattr(agent, field, value)
            self.update(pk=agent.pk, updates=agent.model_dump())

        return searched_profiles

    def match_member_profiles(
        self, leader: Profile, member_num: int = 1
    ) -> List[Profile]:
        members = self.search_profiles(
            condition={'is_member_candidate': True},
            query=leader.bio,
            num=member_num,
            update_fields={
                'is_leader_candidate': False,
                'is_member_candidate': True,
                'is_reviewer_candidate': False,
                'is_chair_candidate': False,
            },
        )
        return members

    def match_reviewer_profiles(
        self, proposal: Proposal, reviewer_num: int = 1
    ) -> List[Profile]:
        reviewers = self.search_profiles(
            condition={'is_reviewer_candidate': True},
            query=proposal.content if proposal.content else '',
            num=reviewer_num,
            update_fields={
                'is_leader_candidate': False,
                'is_member_candidate': False,
                'is_reviewer_candidate': True,
                'is_chair_candidate': False,
            },
        )
        return reviewers

    def match_chair_profiles(
        self, proposal: Proposal, chair_num: int = 1
    ) -> List[Profile]:
        chairs = self.search_profiles(
            condition={'is_chair_candidate': True},
            query=proposal.content,
            num=chair_num,
            update_fields={
                'is_leader_candidate': False,
                'is_member_candidate': False,
                'is_reviewer_candidate': False,
                'is_chair_candidate': True,
            },
        )
        return chairs

    def match_leader_profiles(self, query: str, leader_num: int = 1) -> List[Profile]:
        leaders = self.search_profiles(
            condition={'is_leader_candidate': True},
            query=query,
            num=leader_num,
            update_fields={
                'is_leader_candidate': True,
                'is_member_candidate': False,
                'is_reviewer_candidate': False,
                'is_chair_candidate': False,
            },
        )
        return leaders
