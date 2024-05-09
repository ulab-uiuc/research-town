from typing import Dict

from .env_base import BaseMultiAgentEnv


class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super().__init__(agent_dict)

    def step(self) -> None:
        external_data = self.kb.get_data(10, "machine learning")
        for agent_name, agent in self.agents.items():
            agent.read_paper(external_data=external_data, domain="machine learning")
            agent.review_paper({}, {})
            agent.make_review_decision({}, {})

        self.submit_rebuttal()

    def submit_rebuttal(self) -> None:
        pass
