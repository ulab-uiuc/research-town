from typing import Dict

from .env_base import BaseMultiAgentEnv


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super(PaperSubmissionMultiAgentEnvironment, self).__init__(agent_dict)

    def step(self) -> None:
        external_data = self.kb.get_data(10, "machine learning")
        for agent_name, agent in self.agents.items():
            agent.read_paper(external_data=external_data, domain="machine learning")
            agent.find_collaborators({})
            agent.generate_idea(external_data=external_data, domain="machine learning")
            agent.write_paper([], {})

        self.submit_paper()

    def submit_paper(self) -> None:
        pass
