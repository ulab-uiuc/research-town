import json
import pickle

from beartype.typing import Any, Dict, List, Optional

from ..utils.paper_collector import get_daily_papers
from ..utils.retriever import get_bert_embedding
from .paper_data import PaperProfile


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

    def transfer_to_embedding(self, file_name: str) -> None:
        pickle_file_name = file_name.replace('.json', '.pkl')
        with open(file_name, 'r') as f:
            data = json.load(f)
        paper_dict = {}
        for pk in data.keys():
            paper_dict[pk] = get_bert_embedding([data[pk]['abstract']])
        with open(pickle_file_name, 'wb') as pkl_file:
            pickle.dump(paper_dict, pkl_file)

    def load_from_file(self, file_name: str) -> None:
        pickle_file_name = file_name.replace('.json', '.pkl')
        with open(pickle_file_name, 'rb') as pkl_file:
            self.data_embed = pickle.load(pkl_file)
        with open(file_name, 'r') as f:
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
        data, _ = get_daily_papers(query='ti:' + domain, max_results=num)
        transformed_data = {}
        for date, value in data.items():
            papers = []
            for title, abstract, authors, url, domain, timestamp in zip(
                value['title'],
                value['abstract'],
                value['authors'],
                value['url'],
                value['domain'],
                value['timestamp'],
            ):
                papers.append(
                    {
                        'title': title,
                        'abstract': abstract,
                        'authors': authors,
                        'url': url,
                        'domain': domain,
                        'timestamp': (int)(timestamp),
                    }
                )
            transformed_data[date] = papers
        self.update_db(transformed_data)
