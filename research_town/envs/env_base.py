from abc import ABC, abstractmethod

from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import EnvLogDB, PaperProfileDB, ProgressDB

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class BaseMultiAgentEnv(ABC):
    def __init__(
        self,
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        paper_db: PaperProfileDB,
        config: Config,
    ) -> None:
        self.env_run_num = 0
        self.env_db = env_db
        self.progress_db = progress_db
        self.paper_db = paper_db
        self.config = config
        self.agents: List[BaseResearchAgent] = []

    @abstractmethod
    def on_enter(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def on_exit(self, *args: Any, **kwargs: Any) -> bool:
        pass
