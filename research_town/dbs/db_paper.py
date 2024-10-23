import random
from typing import Any, List, Optional, TypeVar

from transformers import BertModel, BertTokenizer

from ..configs import DatabaseConfig
from ..data.data import Data, Paper
from ..utils.logger import logger
from ..utils.paper_collector import get_recent_papers, get_related_papers
from ..utils.retriever import get_embed
from .db_base import BaseDB

T = TypeVar('T', bound=Data)


class PaperDB(BaseDB[Paper]):
    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__(Paper, config=config, with_embeddings=True)
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

        query_embed = get_embed(
            instructions=[query],
            retriever_tokenizer=self.retriever_tokenizer,
            retriever_model=self.retriever_model,
        )
        query_embeddings = [t.numpy(force=True).squeeze() for t in query_embed]

        match_papers_data = self.database_client.search(
            self.data_class.__name__, query_embeddings, num=num, **conditions
        )[0]
        match_papers = [self.data_class(**d) for d in match_papers_data]

        logger.info(f'Matched papers: {match_papers}')
        return match_papers

    def sample(self, num: int = 1, **conditions: Any) -> List[Paper]:
        papers = self.get(**conditions)
        random.shuffle(papers)
        return papers[:num]

    def add(self, data: Paper) -> None:
        self._initialize_retriever()
        if data.embed is None:
            data.embed = get_embed(
                [data.abstract], self.retriever_tokenizer, self.retriever_model
            )[0]
        super().add(data)
