from beartype.typing import Any, Dict, List, Literal, Optional, Union

from ..configs import Config
from ..dbs import AgentProfile, EnvLogDB, PaperProfileDB, ProgressDB
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class EndMultiAgentEnv(BaseMultiAgentEnv):
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

    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: Optional[List[AgentProfile]] = None,
        agent_roles: Optional[List[Role]] = None,
        agent_models: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.time_step = time_step
        self.stop_flag = stop_flag
        return

    def run(self) -> None:
        return

    def on_exit(self) -> bool:
        if self.stop_flag:
            raise NotImplementedError('Stop signal is not implemented yet.')
        return False
