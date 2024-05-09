from typing import Dict
from .env_base import BaseMultiAgentEnv


class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super().__init__(agent_dict)

    def step(self) -> None:
        for agent_name, agent in self.agents.items():
            paper_summary = agent.read_paper({}, {})
            paper_review = agent.review_paper({}, {})
            review_decision = agent.make_review_decision({}, {})

        self.submit_rebuttal()

    def submit_rebuttal(self) -> None:
        pass
