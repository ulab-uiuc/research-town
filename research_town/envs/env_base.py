from typing import Dict, Generator, Never, Union

from beartype.typing import List

from research_town.utils.logging import logging_decorator

from ..agents.agent_base import BaseResearchAgent
from ..dbs import AgentProfile, EnvLogDB


class BaseMultiAgentEnv(object):
    def __init__(self, agent_profiles: List[AgentProfile]) -> None:
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.agent_profiles: List[AgentProfile] = agent_profiles
        self.db = EnvLogDB()
        self.agents: List[BaseResearchAgent] = []
        self.step_iter_obj: Generator[
            Union[List[Dict[str, str]], List[Never], None], None, None
        ] = self._step()
        for agent_profile in agent_profiles:
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
                )
            )

    def _step(
        self,
    ) -> Generator[Union[List[Dict[str, str]], List[Never], None], None, None]:
        raise NotImplementedError

    @logging_decorator
    def step(self) -> Union[List[Dict[str, str]], List[Never], None]:
        if not self.terminated:
            try:
                return next(self.step_iter_obj)
            except Exception:
                self.turn_number += 1
                if self.turn_number >= self.turn_max:
                    self.terminated = True
                self.step_iter_obj = self._step()
                return next(self.step_iter_obj)
        else:
            return [
                {
                    'text': f"Call 'step()' on a envionment that has terminated ({self.turn_number} / {self.turn_max}).",
                    'level': 'ERROR',
                }
            ]
        return None
