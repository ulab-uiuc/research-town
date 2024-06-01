from beartype.typing import Dict, Generator, List, Union

from ..agents.agent_base import BaseResearchAgent
from ..dbs import AgentProfile, EnvLogDB
from ..utils.logger import logging_decorator

LogType = Union[List[Dict[str, str]], None]


class BaseMultiAgentEnv(object):
    def __init__(self, agent_profiles: List[AgentProfile]) -> None:
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.agent_profiles: List[AgentProfile] = agent_profiles
        self.db = EnvLogDB()
        self.agents: List[BaseResearchAgent] = []
        self.step_obj: Generator[LogType, None, None] = self._step()
        for agent_profile in agent_profiles:
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
                )
            )

    def log(self, message: str, level: str = 'INFO') -> Generator[LogType, None, None]:
        yield [{'text': message, 'level': level}]

    def _step(
        self,
    ) -> Generator[LogType, None, None]:
        raise NotImplementedError

    @logging_decorator
    def step(self) -> LogType:
        if not self.terminated:
            try:
                return next(self.step_obj)
            except Exception:
                self.turn_number += 1
                if self.turn_number >= self.turn_max:
                    self.terminated = True
                self.step_obj = self._step()
                return next(self.step_obj)
        else:
            return next(
                self.log(
                    f"Call 'step()' on a envionment that has terminated ({self.turn_number} / {self.turn_max}).",
                    'ERROR',
                )
            )
