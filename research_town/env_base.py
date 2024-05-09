from typing import Dict

from .agent_base import BaseResearchAgent
from .kb_base import BaseKnowledgeBase


class BaseMultiAgentEnv(object):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        self.agents: Dict[str, BaseResearchAgent] = {}
        self.kb = BaseKnowledgeBase()
        for agent_name, agent in agent_dict.items():
            self.agents[agent_name] = BaseResearchAgent(agent)

    def step(self) -> None:
        raise NotImplementedError
