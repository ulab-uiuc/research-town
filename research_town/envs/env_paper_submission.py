from typing import Dict

from .env_base import BaseMultiAgentEnv


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super(PaperSubmissionMultiAgentEnvironment, self).__init__(agent_dict)

    def step(self) -> None:
        external_data = self.kb.get_data(10, "machine learning")
        abstracts = {}
        for agent_name, agent in self.agents.items():
            trend = agent.read_paper(external_data=external_data, domain="machine learning")
            trends = [trend]
            agent.find_collaborators({})
            ideas = agent.generate_idea(trends=trends, domain="machine learning")
            abstract = agent.write_paper(ideas, external_data)
            abstracts[agent_name] = abstract
        return self.submit_paper(abstracts)

    def submit_paper(self, abstracts: Dict[str, str]) -> Dict[str, str]:
        return abstracts
