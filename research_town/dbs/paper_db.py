from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import json
from ..utils.paper_collector import get_daily_papers

class PaperProfile(BaseModel):
    paper_id: str = Field(index=True)
    title: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)

class PaperProfileDB:
    def __init__(self):
        self.data: Dict[str, PaperProfile] = {}

    def add_paper(self, paper: PaperProfile) -> None:
        self.data[paper.paper_id] = paper

    def update_paper(self, paper_id: str, updates: Dict[str, Optional[str]]) -> bool:
        if paper_id in self.data:
            for key, value in updates.items():
                if value is not None:
                    setattr(self.data[paper_id], key, value)
            return True
        return False

    def get_paper(self, paper_id: str) -> Optional[PaperProfile]:
        return self.data.get(paper_id)

    def delete_paper(self, paper_id: str) -> bool:
        if paper_id in self.data:
            del self.data[paper_id]
            return True
        return False

    def query_papers(self, **conditions) -> List[PaperProfile]:
        result = []
        for paper in self.data.values():
            if all(getattr(paper, key) == value for key, value in conditions.items()):
                result.append(paper)
        return result

    def save_to_file(self, file_name: str) -> None:
        with open(file_name, "w") as f:
            json.dump({pid: paper.dict() for pid, paper in self.data.items()}, f, indent=2)

    def load_from_file(self, file_name: str) -> None:
        with open(file_name, "r") as f:
            data = json.load(f)
            self.data = {pid: PaperProfile(**paper_data) for pid, paper_data in data.items()}

    def update_db(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        for date, papers in data.items():
            for paper_data in papers:
                paper = PaperProfile(**paper_data)
                self.add_paper(paper)

    def fetch_and_add_papers(self, num: int, domain: str) -> None:
        data, _ = get_daily_papers(domain, query=domain, max_results=num)
        self.update_kb(data)