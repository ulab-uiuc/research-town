from typing import Dict, List

from .utils import get_daily_papers


class BaseKnowledgeBase(object):
    def __init__(self) -> None:
        self.data: Dict[str, str] = {}

    def update_kb(self, data: Dict[str, str]) -> None:
        self.data.update(data)

    def add_data(self, data: Dict[str, str]) -> None:
        self.data.update(data)

    def get_data(self, num: int, domain: str) -> Dict[str, Dict[str, List[str]]]:
        data_collector = []
        keywords = dict()
        keywords[domain] = domain

        for topic, keyword in keywords.items():
            data, _ = get_daily_papers(topic, query=keyword, max_results=num)
            data_collector.append(data)
        data_dict = {}
        for data in data_collector:
            for time in data.keys():
                papers = data[time]
                data_dict[time] = papers
        return data_dict
