import json
import pickle
from typing import Dict, Generic, List, Mapping, Optional, Type, TypeVar, Union

from transformers import BertModel, BertTokenizer

from ..configs import Config
from ..utils.agent_collector import collect_paper_abstracts_and_coauthors
from ..utils.agent_prompter import summarize_research_direction_prompting
from ..utils.paper_collector import get_daily_papers
from ..utils.retriever import get_embed, rank_topk
from .profile_data import AgentProfile, BaseProfile, PaperProfile

T = TypeVar('T', bound=BaseProfile)


class BaseProfileDB(Generic[T]):
    def __init__(self, profile_class: Type[T]) -> None:
        self.data: Dict[str, T] = {}
        self.retriever_tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
            'facebook/contriever'
        )
        self.retriever_model: BertModel = BertModel.from_pretrained(
            'facebook/contriever'
        )
        self.profile_class = profile_class

    def add(self, profile: T) -> None:
        self.data[profile.pk] = profile

    def update(
        self, profile_pk: str, updates: Mapping[str, Optional[Union[str, int, float]]]
    ) -> bool:
        if profile_pk in self.data:
            for key, value in updates.items():
                if value is not None:
                    setattr(self.data[profile_pk], key, value)
            return True
        return False

    def delete(self, profile_pk: str) -> bool:
        if profile_pk in self.data:
            del self.data[profile_pk]
            return True
        return False

    def get(self, **conditions: Union[str, int, float]) -> List[T]:
        result = []
        for profile in self.data.values():
            if all(getattr(profile, key) == value for key, value in conditions.items()):
                result.append(profile)
        return result

    def transform_to_embed(self, file_name: str) -> None:
        pickle_file_name = file_name.replace('.json', '.pkl')
        with open(file_name, 'r') as f:
            data = json.load(f)
        profile_dict = {}
        for pk in data.keys():
            profile_dict[pk] = get_embed(
                [data[pk]['abstract']],
                self.retriever_tokenizer,
                self.retriever_model,
            )
        with open(pickle_file_name, 'wb') as pkl_file:
            pickle.dump(profile_dict, pkl_file)

    def match(self, query: str, profiles: List[T], num: int = 1) -> List[str]:
        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        corpus = []
        for profile in profiles:
            if isinstance(profile, PaperProfile):
                corpus.append(profile.abstract if profile.abstract is not None else '')
            elif isinstance(profile, AgentProfile):
                corpus.append(profile.bio if profile.bio is not None else '')
            else:
                raise ValueError('Invalid profile type')
        corpus_embed = get_embed(
            instructions=corpus,
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        index_l = rank_topk(query_data=query_embed, corpus_data=corpus_embed, num=num)
        index_all = [index for index_list in index_l for index in index_list]
        match_pk = [profiles[index].pk for index in index_all]
        return match_pk

    def save_to_file(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            json.dump(
                {pk: profile.model_dump() for pk, profile in self.data.items()},
                f,
                indent=2,
            )

    def load_from_file(self, file_name: str, with_embed: bool = False) -> None:
        if with_embed:
            pickle_file_name = file_name.replace('.json', '.pkl')
            with open(pickle_file_name, 'rb') as pkl_file:
                self.data_embed = pickle.load(pkl_file)
        with open(file_name, 'r') as f:
            data = json.load(f)
            if with_embed:
                for name in data.keys():
                    data[name]['embed'] = self.data_embed[name][0]
            self.data = {
                pk: self.profile_class(**profile_data)
                for pk, profile_data in data.items()
            }


class PaperProfileDB(BaseProfileDB[PaperProfile]):
    def __init__(self) -> None:
        super().__init__(PaperProfile)

    def pull_papers(self, num: int, domain: str) -> None:
        data, _ = get_daily_papers(query='ti:' + domain, max_results=num)
        for value in data.values():
            for title, abstract, authors, url, domain, timestamp in zip(
                value['title'],
                value['abstract'],
                value['authors'],
                value['url'],
                value['domain'],
                value['timestamp'],
            ):
                paper = PaperProfile(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    url=url,
                    domain=domain,
                    timestamp=int(timestamp),
                )
                self.add(paper)


class AgentProfileDB(BaseProfileDB[AgentProfile]):
    def __init__(self) -> None:
        super().__init__(AgentProfile)

    def pull_agents(self, agent_names: List[str], config: Config) -> None:
        for name in agent_names:
            paper_abstracts, collaborators = collect_paper_abstracts_and_coauthors(
                author=name, paper_max_num=10
            )
            personal_info = '; '.join(
                [f"{details['abstract']}" for details in paper_abstracts]
            )
            bio = summarize_research_direction_prompting(
                personal_info=personal_info,
                prompt_template=config.prompt_template.summarize_research_direction,
            )
            agent_profile = AgentProfile(
                name=name,
                bio=bio,
                collaborators=collaborators,
            )
            self.add(agent_profile)
