from typing import List

from ..agents.agent_base import BaseResearchAgent
from ..dbs import AgentProfile, EnvLogDB


class BaseMultiAgentEnv(object):
    def __init__(self, agent_profiles: List[AgentProfile]) -> None:
        self.agent_profiles: List[AgentProfile] = agent_profiles
        self.db = EnvLogDB()
        self.agents: List[BaseResearchAgent] = []
        for agent_profile in agent_profiles:
            self.agents.append(BaseResearchAgent(agent_profile))

    def step(self) -> None:
        raise NotImplementedError
