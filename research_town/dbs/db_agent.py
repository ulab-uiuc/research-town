import json
import pickle
from typing import List, TypeVar

from transformers import BertModel, BertTokenizer

from ..configs import Config
from ..utils.agent_collector import collect_paper_abstracts_and_coauthors
from ..utils.agent_prompter import write_bio_prompting
from ..utils.retriever import get_embed, rank_topk
from .data import AgentProfile, BaseDBData
from .db_base import BaseDB

T = TypeVar('T', bound=BaseDBData)


class AgentProfileDB(BaseDB[AgentProfile]):
    def __init__(self) -> None:
        super().__init__(AgentProfile)
        self.retriever_tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
            'facebook/contriever'
        )
        self.retriever_model: BertModel = BertModel.from_pretrained(
            'facebook/contriever'
        )

    def pull_agents(self, agent_names: List[str], config: Config) -> None:
        for name in agent_names:
            paper_abstracts, collaborators = collect_paper_abstracts_and_coauthors(
                author=name, paper_max_num=10
            )
            publication_info = '; '.join(
                [f"{details['abstract']}" for details in paper_abstracts]
            )
            bio = write_bio_prompting(
                publication_info=publication_info,
                prompt_template=config.prompt_template.write_bio_prompting,
            )
            agent_profile = AgentProfile(
                name=name,
                bio=bio,
                collaborators=collaborators,
            )
            self.add(agent_profile)

    def match(
        self, query: str, agent_profiles: List[AgentProfile], num: int = 1
    ) -> List[AgentProfile]:
        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        corpus = []
        for profile in agent_profiles:
            corpus.append(profile.bio if profile.bio is not None else '')

        corpus_embed = get_embed(
            instructions=corpus,
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        topk_indexes = rank_topk(
            query_data=query_embed, corpus_data=corpus_embed, num=num
        )
        indexes = [index for topk_index in topk_indexes for index in topk_index]
        match_agent_profiles = [agent_profiles[index] for index in indexes]
        return match_agent_profiles

    def transform_to_embed(self, file_name: str) -> None:
        pickle_file_name = file_name.replace('.json', '.pkl')
        with open(file_name, 'r') as f:
            data = json.load(f)
        profile_dict = {}
        for pk in data.keys():
            profile_dict[pk] = get_embed(
                [data[pk]['bio']],
                self.retriever_tokenizer,
                self.retriever_model,
            )
        with open(pickle_file_name, 'wb') as pkl_file:
            pickle.dump(profile_dict, pkl_file)

    def reset_role_avaialbility(self) -> None:
        for profile in self.data.values():
            profile.is_proj_leader_candidate = True
            profile.is_proj_participant_candidate = True
            profile.is_reviewer_candidate = True
            profile.is_chair_candidate = True
            self.update(pk=profile.pk, updates=profile.model_dump())
