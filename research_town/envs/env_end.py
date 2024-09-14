from beartype.typing import Any, Dict, Generator, List, Literal, Tuple, Union

from ..agents import Agent, AgentManager
from ..configs import Config
from ..dbs import Progress
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


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
