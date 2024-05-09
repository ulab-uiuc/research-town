from typing import Dict
from .env_base import BaseMultiAgentEnv


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super(PaperSubmissionMultiAgentEnvironment, self).__init__(agent_dict)

    def step(self) -> None:
        for agent_name, agent in self.agents.items():
            agent.read_paper({}, {})
            agent.find_collaborators({})
            agent.generate_idea({}, {})
            agent.write_paper({}, {})

        self.submit_paper()

    def submit_paper(self) -> None:
        pass
