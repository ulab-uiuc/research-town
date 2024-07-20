from typing import List, Optional, TypeVar

from transformers import BertModel, BertTokenizer

from ..utils.logger import logger
from ..utils.paper_collector import get_daily_papers
from ..utils.retriever import get_embed, rank_topk
from .data import BaseDBData, PaperProfile
from .db_base import BaseDB

T = TypeVar('T', bound=BaseDBData)


class PaperProfileDB(BaseDB[PaperProfile]):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(PaperProfile, load_file_path)
        self.retriever_tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
            'facebook/contriever'
        )
        self.retriever_model: BertModel = BertModel.from_pretrained(
            'facebook/contriever'
        )

    def pull_papers(self, num: int, domain: str) -> None:
        data, _ = get_daily_papers(query=f'ti:{domain}', max_results=num)

        for paper_data in data.values():
            papers = [
                PaperProfile(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    url=url,
                    domain=domain,
                    timestamp=int(timestamp),
                )
                for title, abstract, authors, url, domain, timestamp in zip(
                    paper_data['title'],
                    paper_data['abstract'],
                    paper_data['authors'],
                    paper_data['url'],
                    paper_data['domain'],
                    paper_data['timestamp'],
                )
            ]

            for paper in papers:
                self.add(paper)

    def match(
        self, query: str, paper_profiles: List[PaperProfile], num: int = 1
    ) -> List[PaperProfile]:
        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        corpus_embed = []
        for paper_profile in paper_profiles:
            if paper_profile.pk in self.data_embed:
                corpus_embed.append(self.data_embed[paper_profile.pk])
            else:
                paper_embed = get_embed(
                    instructions=[paper_profile.abstract],
                    retriever_tokenizer=self.retriever_tokenizer,
                    retriever_model=self.retriever_model,
                )[0]
                corpus_embed.append(paper_embed)
        topk_indexes = rank_topk(
            query_embed=query_embed, corpus_embed=corpus_embed, num=num
        )
        indexes = [index for topk_index in topk_indexes for index in topk_index]
        match_paper_profiles = [paper_profiles[index] for index in indexes]
        logger.info(f'Matched papers: {match_paper_profiles}')
        return match_paper_profiles

    def transform_to_embed(self) -> None:
        for paper_pk in self.data:
            self.data_embed[paper_pk] = get_embed(
                [self.data[paper_pk].abstract],
                self.retriever_tokenizer,
                self.retriever_model,
            )[0]
