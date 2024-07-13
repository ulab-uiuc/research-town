from abc import ABC, abstractmethod

from beartype.typing import Dict, List, Literal, Optional, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import AgentProfile, EnvLogDB, PaperProfileDB, ProgressDB

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
    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: Optional[List[AgentProfile]] = None,
        agent_roles: Optional[List[Role]] = None,
        agent_models: Optional[List[str]] = None,
    ) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def on_exit(self) -> bool:
        pass
