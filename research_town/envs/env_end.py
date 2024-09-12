from beartype.typing import Any, Dict, List, Literal, Union

from ..configs import Config
from ..dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from .env_base import BaseEnv



class EndEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        profile_db: ProfileDB,
        config: Config,
    ) -> None:
        super().__init__(
            name=name,
            log_db=log_db,
            progress_db=progress_db,
            paper_db=paper_db,
            profile_db=profile_db,
            config=config,
        )

    def on_enter(
        self,
        time_step: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.time_step = time_step
        return

    def run(self) -> None:
        return

    def on_exit(self) -> str:
        return 'end'
