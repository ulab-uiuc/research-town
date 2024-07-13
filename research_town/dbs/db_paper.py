import json
import pickle
from typing import List, TypeVar

from transformers import BertModel, BertTokenizer

from ..utils.paper_collector import get_daily_papers
from ..utils.retriever import get_embed, rank_topk
from .data import BaseDBData, PaperProfile
from .db_base import BaseDB

T = TypeVar('T', bound=BaseDBData)


class PaperProfileDB(BaseDB[PaperProfile]):
    def __init__(self) -> None:
        super().__init__(PaperProfile)
        self.retriever_tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
            'facebook/contriever'
        )
        self.retriever_model: BertModel = BertModel.from_pretrained(
            'facebook/contriever'
        )

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

    def match(
        self, query: str, paper_profiles: List[PaperProfile], num: int = 1
    ) -> List[PaperProfile]:
        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        corpus = []
        for profile in paper_profiles:
            corpus.append(profile.abstract if profile.abstract is not None else '')
        corpus_embed = get_embed(
            instructions=corpus,
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        topk_indexes = rank_topk(
            query_embed=query_embed, corpus_embed=corpus_embed, num=num
        )
        indexes = [index for topk_index in topk_indexes for index in topk_index]
        match_paper_profiles = [paper_profiles[index] for index in indexes]
        return match_paper_profiles

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
