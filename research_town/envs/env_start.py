from collections import Counter

from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import AgentProfile, EnvLogDB, PaperProfileDB, ProgressDB
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class StartMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(
        self,
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        paper_db: PaperProfileDB,
        config: Config,
    ) -> None:
        super().__init__(
            env_db=env_db,
            progress_db=progress_db,
            paper_db=paper_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
        agent_models: List[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.time_step = time_step
        self.stop_flag = stop_flag

        assert len(agent_profiles) == len(agent_roles)

        for agent_profile, agent_role, agent_model in zip(
            agent_profiles, agent_roles, agent_models
        ):
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    agent_role=agent_role,
                    model_name=agent_model,
                )
            )

        if 'proj_leader' not in agent_roles:
            raise ValueError('At least one proj_leader is required to submit paper.')
        if 'proj_participant' in agent_roles:
            raise ValueError(
                'Proj_participant role is not allowed in paper submission.'
            )
        if 'reviewer' in agent_roles:
            raise ValueError('Reviewer role is not allowed in paper submission.')
        if 'chair' in agent_roles:
            raise ValueError('Chair role is not allowed in paper submission.')

        counter = Counter(agent_roles)
        if counter['proj_leader'] != 1:
            raise ValueError('Exactly one proj_leader is required to submit paper.')

        self.proj_leader = [
            agent for agent in self.agents if agent.role == 'proj_leader'
        ][0]

    def run(self) -> None:
        return

    def on_exit(self) -> bool:
        if self.stop_flag:
            raise NotImplementedError('Stop signal is not implemented yet.')
        return True
