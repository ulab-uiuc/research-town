from typing import List, Tuple, Dict


class BaseResearchAgent(object):
    def __init__(self, name: str) -> None:
        self.profile = self.get_profile(name)
        self.memory: Dict[str, str] = {}

    def get_profile(self, name: str) -> Dict[str, str]:
        return {'name': 'John Doe', 'age': '25', 'location': 'New York'}

    def communicate(self, message: Dict[str, str]) -> str:
        return 'hello'

    def read_paper(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return 'reading paper'
    
    def find_collaborators(self, input: Dict[str, str]) -> List[str]:
        return ['Alice', 'Bob', 'Charlie']
    
    def generate_idea(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return 'idea'
    
    def write_paper(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return 'writing paper'
    
    def review_paper(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return 'review comments'
    
    def make_review_decision(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return 'accept'

