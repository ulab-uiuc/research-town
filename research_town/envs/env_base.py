from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, Tuple

from ..configs import Config
from ..dbs import Profile, Progress


class BaseEnv(ABC):
    def __init__(self, name: str, config: Config) -> None:
        self.name = name
        self.config = config
        self.env_run_num = 0

    @abstractmethod
    def on_enter(self, **context: Any) -> None:
        pass

    @abstractmethod
    def run(self) -> Generator[Tuple[Progress, Profile], None, None] | None:
        pass

    @abstractmethod
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        pass
