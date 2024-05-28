from typing import List

from ..agents.agent_base import BaseResearchAgent
from ..dbs import AgentProfile, EnvLogDB


class BaseMultiAgentEnv(object):
    def __init__(self, agent_profiles: List[AgentProfile], callback=None) -> None:
        self.agent_profiles: List[AgentProfile] = agent_profiles
        self.db = EnvLogDB()
        self.agents: List[BaseResearchAgent] = []
        self.callback = callback
        for agent_profile in agent_profiles:
            self.agents.append(BaseResearchAgent(agent_profile))
        if self.callback:
            self.callback()

    def _step(self) -> None:
        raise NotImplementedError
        
    def step(self) -> None:
        self._step()
        if self.callback:
            self.callback()
