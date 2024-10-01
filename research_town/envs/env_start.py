from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple, Union

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from .env_base import BaseEnv


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
        self.contexts = context['contexts']
        contexts_to_text = ''
        for idx, context in enumerate(self.contexts):
            contexts_to_text += f'Paper {idx + 1}: \n\n{context}\n\n'
        self.leader = self.agent_manager.find_leader(task=contexts_to_text)

    def run(
        self,
    ) -> Generator[
        Tuple[
            Union[
                List[Insight],
                List[Idea],
                List[Proposal],
                List[Review],
                List[Rebuttal],
                List[MetaReview],
            ],
            Agent,
        ],
        None,
        None,
    ]:
        if False:
            yield

    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        return 'start_proposal', {'leader': self.leader, 'contexts': self.contexts}
