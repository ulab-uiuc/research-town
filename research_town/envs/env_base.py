from abc import ABC, abstractmethod

from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import AgentDB, LogDB, PaperDB, ProgressDB

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class BaseEnv(ABC):
    def __init__(
        self,
        name: str,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        agent_db: AgentDB,
        config: Config,
    ) -> None:
        self.name = name
        self.env_run_num = 0
        self.log_db = log_db
        self.progress_db = progress_db
        self.paper_db = paper_db
        self.agent_db = agent_db
        self.config = config
        self.agents: List[BaseResearchAgent] = []

    @abstractmethod
    def on_enter(
        self,
        time_step: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        pass

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def on_exit(self, *args: Any, **kwargs: Any) -> str:
        pass
