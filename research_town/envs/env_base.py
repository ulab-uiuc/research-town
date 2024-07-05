from beartype.typing import Dict, List, Literal, Union

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
        assert len(agent_profiles) == len(agent_roles)
        for agent_profile, agent_role in zip(agent_profiles, agent_roles):
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    agent_role=agent_role,
                    model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
                )
            )

    def run(
        self,
    ) -> None:
        raise NotImplementedError
