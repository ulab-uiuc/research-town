from typing import List, Optional, TypeVar

import torch
from transformers import BertModel, BertTokenizer

from ..utils.logger import logger
from ..utils.paper_collector import get_daily_papers
from ..utils.retriever import get_embed, rank_topk
from .data import Data, Paper
from .db_base import BaseDB

T = TypeVar('T', bound=Data)


class PaperDB(BaseDB[Paper]):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(Paper, load_file_path)
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
                Paper(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    url=url,
                    domain=domain,
                    timestamp=int(timestamp),
                    section_contents=section_contents,
                    bibliography=bibliography,
                    figure_captions=figure_captions,
                    table_captions=table_captions,
                )
                for title, abstract, authors, url, domain, timestamp, section_contents, bibliography, figure_captions, table_captions in zip(
                    paper_data['title'],
                    paper_data['abstract'],
                    paper_data['authors'],
                    paper_data['url'],
                    paper_data['domain'],
                    paper_data['timestamp'],
                    paper_data['section_contents'],
                    paper_data['bibliography'],
                    paper_data['figure_captions'],
                    paper_data['table_captions'],
                )
            ]

            for paper in papers:
                self.add(paper)

    def match(self, query: str, papers: List[Paper], num: int = 1) -> List[Paper]:
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

    def transform_to_embed(self) -> None:
        for paper_pk in self.data:
            self.data_embed[paper_pk] = get_embed(
                [self.data[paper_pk].abstract],
                self.retriever_tokenizer,
                self.retriever_model,
            )[0]
