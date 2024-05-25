from typing import Dict, List

from ..agents.agent_base import BaseResearchAgent
from ..dbs.kb_base import BaseKnowledgeBase


class BaseMultiAgentEnv(object):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        self.agents: List[BaseResearchAgent] = []
        self.kb = BaseKnowledgeBase()
        for _, agent_name in agent_dict.items():
            self.agents.append(BaseResearchAgent(agent_name))

    def step(self) -> None:
        raise NotImplementedError
