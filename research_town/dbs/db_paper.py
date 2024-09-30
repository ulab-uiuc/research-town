import random
from typing import Any, List, Optional, TypeVar

import torch
from transformers import BertModel, BertTokenizer

from ..data.data import Data, Paper
from ..utils.logger import logger
from ..utils.paper_collector import get_recent_papers, get_related_papers
from ..utils.retriever import get_embed, rank_topk
from .db_base import BaseDB

T = TypeVar('T', bound=Data)


class PaperDB(BaseDB[Paper]):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(Paper, load_file_path)
        self.retriever_tokenizer: Optional[BertTokenizer] = None
        self.retriever_model: Optional[BertModel] = None

    def _initialize_retriever(self) -> None:
        if self.retriever_tokenizer is None or self.retriever_model is None:
            self.retriever_tokenizer = BertTokenizer.from_pretrained(
                'facebook/contriever'
            )
            self.retriever_model = BertModel.from_pretrained('facebook/contriever')

    def pull_papers(self, num: int, domain: Optional[str] = None) -> List[Paper]:
        papers = get_recent_papers(domain=domain, max_results=num)
        for paper in papers:
            self.add(paper)
        logger.info(f'Pulled {num} papers')
        return papers

    def search_papers(
        self,
        num: int,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        author: Optional[str] = None,
    ) -> List[Paper]:
        papers = get_related_papers(
            query=query, domain=domain, author=author, num_results=num
        )
        for paper in papers:
            self.add(paper)
        logger.info(f'Searched {num} papers')
        return papers

    def match(self, query: str, num: int = 1, **conditions: Any) -> List[Paper]:
        self._initialize_retriever()
        papers = self.get(**conditions)

        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        corpus_embed: List[torch.Tensor] = []

        for paper in papers:
            if paper.pk in self.data_embed:
                corpus_embed.append(self.data_embed[paper.pk])
            else:
                paper_embed = get_embed(
                    instructions=[paper.abstract],
                    retriever_tokenizer=self.retriever_tokenizer,
                    retriever_model=self.retriever_model,
                )[0]
                corpus_embed.append(paper_embed)
        topk_indexes = rank_topk(
            query_embed=query_embed, corpus_embed=corpus_embed, num=num
        )
        indexes = [index for topk_index in topk_indexes for index in topk_index]
        match_papers = [papers[index] for index in indexes]
        logger.info(f'Matched papers: {match_papers}')
        return match_papers

    def sample(self, num: int = 1, **conditions: Any) -> List[Paper]:
        papers = self.get(**conditions)
        random.shuffle(papers)
        return papers[:num]

    def transform_to_embed(self) -> None:
        self._initialize_retriever()

        for paper_pk in self.data:
            self.data_embed[paper_pk] = get_embed(
                [self.data[paper_pk].abstract],
                self.retriever_tokenizer,
                self.retriever_model,
            )[0]
