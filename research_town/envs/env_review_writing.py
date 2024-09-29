from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Progress, Rebuttal, Review
from ..dbs import LogDB, PaperDB, ProgressDB
from .env_base import BaseEnv


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
        self.chair = self.agent_manager.sample_chair()
        self.reviewers = self.agent_manager.sample_reviewers()

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        self.env_run_num += 1
        if self.env_run_num > self.config.param.max_env_run_num:
            return 'error', {}
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
                proposal=self.proposal,
                config=self.config,
            )
            self.reviews.append(review)
            yield review, reviewer

        # Rebuttal Submitting
        self.rebuttals: List[Rebuttal] = []
        for review in self.reviews:
            rebuttal = self.leader.write_rebuttal(
                proposal=self.proposal,
                review=review,
                config=self.config,
            )
            self.rebuttals.append(rebuttal)
            yield rebuttal, self.leader

        # Paper Meta Reviewing
        metareview = self.chair.write_metareview(
            proposal=self.proposal,
            reviews=self.reviews,
            config=self.config,
        )
        yield metareview, self.chair

        self.metareview = metareview

        return None
