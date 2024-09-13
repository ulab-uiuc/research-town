from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union, Tuple

from ..agents.agent_base import ResearchAgent
from ..configs import Config
from ..dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class StartEnv(BaseEnv):
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

    @beartype
    def on_enter(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        task = kwargs['task']
        leader_profile = self.profile_db.match_leader_profiles(
            query=task, leader_num=1
        )[0]
        self.leader = ResearchAgent(
            agent_profile=leader_profile,
            agent_role='leader',
            model_name=self.config.param.base_llm,
        )

    def run(self) -> None:
        return

    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        return 'start_proposal', {}
