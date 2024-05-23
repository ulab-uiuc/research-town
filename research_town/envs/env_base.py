from typing import Dict

from ..agents.agent_base import BaseResearchAgent
from ..kbs.kb_base import BaseKnowledgeBase
from ..kbs.profile import AgentProfile


class BaseMultiAgentEnv(object):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        self.agents: Dict[str, BaseResearchAgent] = {}
        self.profiles: Dict[str, AgentProfile] = {}
        self.kb = BaseKnowledgeBase()
        for agent_id, agent_name in agent_dict.items():
            self.agents[agent_id] = BaseResearchAgent(agent_name)
            self.profiles[agent_id] = AgentProfile()
            self.profiles[agent_id].agent_id = agent_id
            self.profiles[agent_id].name = agent_name
            self.profiles[agent_id].profile = self.agents[agent_id].get_profile(agent_name)["profile"]

    def step(self) -> None:
        raise NotImplementedError
