from typing import List, Tuple, Dict
from .agent_base import BaseResearchAgent


class BaseMultiAgentEnv(object):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        self.agents: Dict[str, BaseResearchAgent] = {}
        for agent_name, agent in agent_dict.items():
            self.agents[agent_name] = BaseResearchAgent(agent)

    def step(self) -> None:
        raise NotImplementedError