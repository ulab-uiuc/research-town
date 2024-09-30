import random
from typing import Any, List, Literal, Optional, TypeVar

import requests
import torch
from transformers import BertModel, BertTokenizer

from ..data.data import Data, Paper
from ..utils.logger import logger
from ..utils.paper_collector import get_recent_papers, get_related_papers
from ..utils.retriever import get_embed, rank_topk
from .db_base import BaseDB

T = TypeVar('T', bound=Data)

Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class PaperDB(BaseDB[Paper]):
    SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/search'

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

    def match_offline(self, query: str, num: int = 1, **conditions: Any) -> List[Paper]:
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
                self.data_embed[paper.pk] = paper_embed

        topk_indexes = rank_topk(
            query_embed=query_embed, corpus_embed=corpus_embed, num=num
        )
        indexes = [index for topk_index in topk_indexes for index in topk_index]
        match_papers = [papers[index] for index in indexes]

        logger.info(f'Matched papers (offline): {match_papers}')
        return match_papers

    def match_online(
        self,
        query: Optional[str] = None,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        num: int = 1,
    ) -> List[Paper]:
        if not query and not name:
            logger.warning('No query or name provided for online matching.')
            return []

        search_query = query if query else name
        params = {
            'query': search_query,
            'fields': 'title, authors, abstract, url, domain, timestamp, sections, bibliography',
            'limit': num,
        }

        try:
            response = requests.get(self.SEMANTIC_SCHOLAR_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Semantic Scholar API request failed: {e}')
            return []

        matched_papers = []
        for paper_data in data.get('data', []):
            paper_fields = paper_data.get('fieldsOfStudy', [])
            if domain and domain not in paper_fields:
                continue

            paper = Paper(
                title=paper_data.get('title', ''),
                abstract=paper_data.get('abstract', ''),
                authors=[author['name'] for author in paper_data.get('authors', [])],
                url=paper_data.get('url', ''),
                domain=domain if domain else ', '.join(paper_fields),
                timestamp=paper_data.get('year', 0),
                sections=None,
                bibliography=None,
            )
            matched_papers.append(paper)

            self.add(paper)
        logger.info(f'Matched papers (online): {matched_papers}')
        return matched_papers

    def match(
        self,
        query: Optional[str] = None,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        num: int = 1,
        **conditions: Any,
    ) -> List[Paper]:
        results: List[Paper] = []

        if query:
            offline_results = self.match_offline(query=query, num=num, **conditions)
            results.extend(offline_results)
            if len(results) >= num:
                return results[:num]

        if name:
            offline_results = self.match_offline(
                query=name, num=num - len(results), **conditions
            )
            results.extend(offline_results)
            if len(results) >= num:
                return results[:num]

        if len(results) < num and (query or name):
            online_results = self.match_online(
                query=query, name=name, domain=domain, num=num - len(results)
            )
            results.extend(online_results)

        logger.info(f'Total matched papers: {results}')
        return results[:num]

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
