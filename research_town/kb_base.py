from typing import List, Tuple, Dict
from utils import *

class BaseKnowledgeBase(object):
    def __init__(self) -> None:
        self.data: Dict[str, str] = {}

    def update_kb(self, data: Dict[str, str]) -> None:
        self.data.update(data)
    
    def add_data(self, data: Dict[str, str]) -> None:
        self.data.update(data)
    
    def get_data(self, num: str,domain:str):
        data_collector = []
        keywords = dict()
        keywords[domain] = domain

        for topic, keyword in keywords.items():
            # print("Keyword: " + topic)
            data, _ = get_daily_papers(topic, query=keyword, max_results=num)
            data_collector.append(data)
        data_dict = {}
        for data in data_collector:
            for time in data.keys():
                papers = data[time]
                # print(papers.published)
                data_dict[time.strftime("%m/%d/%Y")] = papers
        return data_dict

