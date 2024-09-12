from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import AgentDB, LogDB, PaperDB, ProgressDB
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
        agent_db: AgentDB,
        config: Config,
    ) -> None:
        super().__init__(
            name=name,
            log_db=log_db,
            progress_db=progress_db,
            paper_db=paper_db,
            agent_db=agent_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        task = kwargs['task']
        leader_profile = self.agent_db.invite_leaders(
            query=kwargs['task'], leader_num=1
        )[0]
        self.time_step = time_step
        self.leader = BaseResearchAgent(
            agent_profile=leader_profile,
            agent_role='leader',
            model_name=self.config.param.base_llm,
        )

    def run(self) -> None:
        return

    def on_exit(self) -> str:
        return 'start_proposal'
