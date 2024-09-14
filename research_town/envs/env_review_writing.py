from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Literal, Tuple, Union

from ..agents import ResearchAgentManager
from ..configs import Config
from ..dbs import LogDB, PaperDB, Profile, Progress, ProgressDB, Rebuttal, Review
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
        agent_manager: ResearchAgentManager,
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
                'meta_review': self.meta_review,
                'leader': self.leader,
            }

    @beartype
    def run(self) -> Generator[Tuple[Progress, Profile], None, None] | None:
        # Review Writing
        self.reviews: List[Review] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper=self.proposal,
                config=self.config,
            )
            yield review, reviewer.profile

        # Rebuttal Submitting
        self.rebuttals: List[Rebuttal] = []
        for review in self.reviews:
            rebuttal = self.leader.write_rebuttal(
                paper=self.proposal,
                review=review,
                config=self.config,
            )
            yield rebuttal, self.leader.profile

        # Paper Meta Reviewing
        meta_review = self.chair.write_meta_review(
            paper=self.proposal,
            reviews=self.reviews,
            rebuttals=self.rebuttals,
            config=self.config,
        )
        yield meta_review, self.chair.profile

        self.meta_review = meta_review

        return None
