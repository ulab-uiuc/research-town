from typing import List, Tuple, Dict


class PaperSubmissionMultiAgentEnvironment(object):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        self.agent_dict = agent_dict

    def step(self) -> None:
        for agent_name, agent in self.agent_dict.items():
            agent.read_paper({}, {})
            agent.find_collaborators({})
            agent.generate_idea({}, {})
            agent.write_paper({}, {})
        
        self.submit_paper()
    
    def submit_paper(self):
        pass