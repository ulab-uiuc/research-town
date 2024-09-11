from beartype.typing import Any, Dict, List, Literal, Optional, Union

from ..configs import Config
from ..dbs import LogDB, PaperDB, ProgressDB, Researcher
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class EndEnv(BaseEnv):
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

    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: Optional[List[Researcher]] = None,
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

    def on_exit(self) -> str:
        return 'end'
