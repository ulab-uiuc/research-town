from typing import List, Tuple, Dict

class BaseKnowledgeBase(object):
    def __init__(self) -> None:
        self.data = {}

    def update_kb(self, data: Dict[str, str]) -> None:
        self.data.update(data)
    
    def add_data(self, data: Dict[str, str]) -> None:
        self.data.update(data)
    
    def get_data(self, key: str) -> str:
        return self.data[key]