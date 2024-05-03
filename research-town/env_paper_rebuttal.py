from typing import List, Tuple, Dict

class PaperRebuttalMultiAgentEnvironment(object):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        self.agent_dict = agent_dict

    def step(self) -> None:
        for agent_name, agent in self.agent_dict.items():
            agent.read_paper({}, {})
            agent.review_paper({}, {})
            agent.make_review_decision({}, {})
        
        self.submit_rebuttal()
    
    def submit_rebuttal(self):
        pass