from collections import Counter

from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import LogDB, PaperDB, ProgressDB, Researcher
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class StartEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        env_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        config: Config,
    ) -> None:
        super().__init__(
            name=name,
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
        agent_profiles: List[Researcher],
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

        if 'leader' not in agent_roles:
            raise ValueError('At least one leader is required to submit paper.')
        if 'member' in agent_roles:
            raise ValueError('member role is not allowed in paper submission.')
        if 'reviewer' in agent_roles:
            raise ValueError('Reviewer role is not allowed in paper submission.')
        if 'chair' in agent_roles:
            raise ValueError('Chair role is not allowed in paper submission.')

        counter = Counter(agent_roles)
        if counter['leader'] != 1:
            raise ValueError('Exactly one leader is required to submit paper.')

        self.leader = [agent for agent in self.agents if agent.role == 'leader'][0]

    def run(self) -> None:
        return

    def on_exit(self) -> str:
        return 'start_proposal'
