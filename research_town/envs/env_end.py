from beartype.typing import Any, Dict, List, Literal, Union, Tuple

from ..configs import Config
from ..dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


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
        *args: Any,
        **kwargs: Any,
    ) -> None:
        return

    def run(self) -> None:
        return

    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        return 'end', {}
