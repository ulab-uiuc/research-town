import json
import uuid
import pickle
from beartype.typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..utils.paper_collector import get_daily_papers
import torch

class PaperProfile(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    authors: Optional[List[str]] = Field(default=[])
    url: Optional[str] = Field(default=None)
    timestamp: Optional[int] = Field(default=None)
    section_contents: Optional[Dict[str, str]] = Field(default=None)
    table_captions: Optional[Dict[str, str]] = Field(default=None)
    figure_captions: Optional[Dict[str, str]] = Field(default=None)
    bibliography: Optional[Dict[str, str]] = Field(default=None)
    keywords: Optional[List[str]] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    references: Optional[List[Dict[str, str]]] = Field(default=None)
    citation_count: Optional[int] = Field(default=0)
    award: Optional[str] = Field(default=None)
    embed: Optional[Any] = Field(default=None)
    class Config:
        arbitrary_types_allowed = True
class PaperProfileDB:
    def __init__(self) -> None:
        self.data: Dict[str, PaperProfile] = {}

    def add_paper(self, paper: PaperProfile) -> None:
        self.data[paper.pk] = paper

    def update_paper(self, paper_pk: str, updates: Dict[str, Any]) -> bool:
        if paper_pk in self.data:
            for key, value in updates.items():
                if value is not None:
                    setattr(self.data[paper_pk], key, value)
            return True
        return False

    def get_paper(self, paper_pk: str) -> Optional[PaperProfile]:
        return self.data.get(paper_pk)

    def delete_paper(self, paper_pk: str) -> bool:
        if paper_pk in self.data:
            del self.data[paper_pk]
            return True
        return False

    def query_papers(self, **conditions: Dict[str, Any]) -> List[PaperProfile]:
        result = []
        for paper in self.data.values():
            if all(getattr(paper, key) == value for key, value in conditions.items()):
                result.append(paper)
        return result

    def save_to_file(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            json.dump(
                {pk: paper.model_dump() for pk, paper in self.data.items()}, f, indent=2
            )

    def load_from_file(self, file_name: str) -> None:
        with open(file_name + '.pkl', 'rb') as pkl_file:
            self.data_embed = pickle.load(pkl_file)
        with open(file_name + ".json", 'r') as f:
            data = json.load(f)
            for name in data.keys():
                data[name]['embed'] = self.data_embed[name][0]
            self.data = {
                pk: PaperProfile(**paper_data) for pk, paper_data in data.items()
            }

    def update_db(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        for date, papers in data.items():
            for paper_data in papers:
                paper = PaperProfile(**paper_data)
                self.add_paper(paper)

    def fetch_and_add_papers(self, num: int, domain: str) -> None:
        data, _ = get_daily_papers(domain, query=domain, max_results=num)
        transformed_data = {}
        for date, value in data.items():
            papers = []
            papers.append({'abstract': value['abstract']})
            papers.append({'info': value['info']})
            transformed_data[date] = papers
        self.update_db(transformed_data)
