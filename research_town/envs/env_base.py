from beartype.typing import Dict, Generator, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..dbs import AgentProfile, EnvLogDB, ProgressDB

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class BaseMultiAgentEnv(object):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
    ) -> None:
        self.env_run_number = 0
        self.max_env_run_number = 1
        self.terminated = False
        self.agent_profiles: List[AgentProfile] = agent_profiles
        self.env_db = EnvLogDB()
        self.progress_db = ProgressDB()
        self.agents: List[BaseResearchAgent] = []
        # self.step_obj: Generator[LogType, None, None] = self._step()
        assert len(agent_profiles) == len(agent_roles)
        for agent_profile, agent_role in zip(agent_profiles, agent_roles):
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    agent_role=agent_role,
                    model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
                )
            )

    def log(self, message: str, level: str = 'INFO') -> Generator[LogType, None, None]:
        yield [{'text': message, 'level': level}]

    def step(
        self,
    ) -> None:
        raise NotImplementedError

    # @logging_decorator
    # def step(self) -> LogType:
    #     if not self.terminated:
    #         try:
    #             return next(self.step_obj)
    #         except Exception:
    #             if self.env_run_number < self.max_env_run_number:
    #                 self.env_run_number += 1
    #             else:
    #                 self.terminated = True
    #             self.step_obj = self._step()
    #             return next(self.step_obj)
    #     else:
    #         return next(
    #             self.log(
    #                 f"Call 'step()' on a environment that has terminated ({self.env_run_number} / {self.max_env_run_number}).",
    #                 'ERROR',
    #             )
    #         )
