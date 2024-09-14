from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Literal, Tuple, Union

from ..agents import Agent, AgentManager
from ..configs import Config
from ..dbs import LogDB, PaperDB, Progress, ProgressDB, Rebuttal, Review
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class ReviewWritingEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        config: Config,
        agent_manager: AgentManager,
    ) -> None:
        super().__init__(
            name=name,
            config=config,
        )
        self.log_db = log_db
        self.progress_db = progress_db
        self.paper_db = paper_db
        self.agent_manager = agent_manager

    @beartype
    def on_enter(
        self,
        **context: Any,
    ) -> None:
        self.proposal = context['proposal']
        self.leader = context['leader']
        self.chair = self.agent_manager.find_chair(self.proposal)
        self.reviewers = self.agent_manager.find_reviewers(self.proposal)

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        self.env_run_num += 1
        if self.env_run_num > self.config.param.max_env_run_num:
            return 'end', {}
        else:
            return 'proposal_accept', {
                'metareview': self.metareview,
                'leader': self.leader,
            }

    @beartype
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        # Review Writing
        self.reviews: List[Review] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper=self.proposal,
                config=self.config,
            )
            yield review, reviewer

        # Rebuttal Submitting
        self.rebuttals: List[Rebuttal] = []
        for review in self.reviews:
            rebuttal = self.leader.write_rebuttal(
                paper=self.proposal,
                review=review,
                config=self.config,
            )
            yield rebuttal, self.leader

        # Paper Meta Reviewing
        metareview = self.chair.write_metareview(
            paper=self.proposal,
            reviews=self.reviews,
            rebuttals=self.rebuttals,
            config=self.config,
        )
        yield metareview, self.chair

        self.metareview = metareview

        return None
