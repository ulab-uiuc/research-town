from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import MetaReview, Progress, Rebuttal, Review
from ..dbs import LogDB, PaperDB, ProgressDB
from .env_base import BaseEnv


class ReviewWritingEnvPaperText(BaseEnv):
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
        self.leader = context.get('leader', self.agent_manager.sample_leader())
        self.chair = context.get('chair', self.agent_manager.sample_chair())
        self.reviewers = context.get('reviewers', self.agent_manager.sample_reviewers())
        self.paper_text = context['paper_text']
        self.metareviews: List[MetaReview] = []

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        self.env_run_num += 1
        if self.env_run_num > self.config.param.max_env_run_num:
            return 'error', {}
        else:
            return 'paper_accept', {
                'metareviews': self.metareviews,
                'leader': self.leader,
            }

    @beartype
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        # Review Writing
        self.reviews: List[Review] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper_text=self.paper_text,
                config=self.config,
            )
            self.reviews.append(review)
            yield review, reviewer

        # Rebuttal Submitting
        self.rebuttals: List[Rebuttal] = []
        for review in self.reviews:
            rebuttal = self.leader.write_rebuttal(
                paper_text=self.paper_text,
                review=review,
                config=self.config,
            )
            self.rebuttals.append(rebuttal)
            yield rebuttal, self.leader

        # Paper Meta Reviewing
        metareview = self.chair.write_metareview(
            paper_text=self.paper_text,
            reviews=self.reviews,
            config=self.config,
        )
        self.metareviews.append(metareview)
        yield metareview, self.chair
