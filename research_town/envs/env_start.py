from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Literal, Tuple, Union

from ..agents import AgentManager
from ..configs import Config
from ..dbs import Profile, Progress
from .env_base import BaseEnv
from ..agents import Agent

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class StartEnv(BaseEnv):
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

    @beartype
    def on_enter(
        self,
        **context: Any,
    ) -> None:
        task = context['task']
        self.leader = self.agent_manager.find_leader(task)

    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        return None

    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        return 'start_proposal', {'leader': self.leader}
