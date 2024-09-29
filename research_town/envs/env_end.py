from beartype.typing import Any, Dict, Generator, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Progress
from .env_base import BaseEnv


class EndEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        config: Config,
        agent_manager: AgentManager,
    ) -> None:
        super().__init__(
            name=name,
            config=config,
        )
        self.agent_manager = agent_manager

    def on_enter(self, **context: Any) -> None:
        return

    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        if False:
            yield

    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        return 'end', {}
