from typing import Dict

from .env_base import BaseMultiAgentEnv


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super(PaperSubmissionMultiAgentEnvironment, self).__init__(agent_dict)

    def step(self) -> None:
        papers = self.kb.get_data(10, "machine learning")
        for agent in self.agents:
            agent.read_paper(papers=papers, domain="machine learning")
            agent.find_collaborators({})
            agent.generate_idea(papers=papers, domain="machine learning")
            agent.write_paper([], {})

        self.submit_paper()

    def submit_paper(self) -> None:
        pass
