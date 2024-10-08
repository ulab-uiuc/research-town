from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, Tuple

from ..agents import Agent
from ..configs import Config
from ..data import Progress


class BaseEnv(ABC):
    def __init__(self, name: str, config: Config) -> None:
        self.name = name
        self.config = config
        self.env_run_num = 0

    @abstractmethod
    def on_enter(self, **context: Any) -> None:
        pass

    @abstractmethod
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        pass

    @abstractmethod
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        pass
