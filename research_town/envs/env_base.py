from abc import ABC, abstractmethod

from beartype.typing import Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import EnvLogDB, ProgressDB

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class BaseMultiAgentEnv(ABC):
    def __init__(
        self,
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        config: Config,
    ) -> None:
        self.env_run_num = 0
        self.env_db = env_db
        self.progress_db = progress_db
        self.config = config

    @abstractmethod
    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agents: List[BaseResearchAgent],
        agent_roles: List[Role],
    ) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def on_exit(self) -> bool:
        pass
