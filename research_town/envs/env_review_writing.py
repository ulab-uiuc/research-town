from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import MetaReview, Progress, Review
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
        if 'leader' not in context or context['leader'] is None:
            context['leader'] = self.agent_manager.sample_leader()
        if 'chair' not in context or context['chair'] is None:
            context['chair'] = self.agent_manager.sample_chair()
        if 'reviewers' not in context or context['reviewers'] is None:
            context['reviewers'] = self.agent_manager.sample_reviewers()

        self.leader = context['leader']
        self.chair = context['chair']
        self.reviewers = context['reviewers']

        self.proposals = context['proposals']

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        self.env_run_num += 1
        if self.env_run_num > self.config.param.max_env_run_num:
            return 'error', {}
        else:
            return 'proposal_accept', {
                'metareviews': self.metareviews,
                'leader': self.leader,
            }

    @beartype
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        self.metareviews: List[MetaReview] = []
        for proposal in self.proposals:
            # Review Writing
            self.reviews: List[Review] = []
            for reviewer in self.reviewers:
                review = reviewer.write_review(
                    profile=reviewer.profile,
                    proposal=proposal,
                    config=self.config,
                )
                self.reviews.append(review)
                yield review, reviewer

            # Rebuttal Submitting
            # self.rebuttals: List[Rebuttal] = []
            # for review in self.reviews:
            #     rebuttal = self.leader.write_rebuttal(
            #         proposal=proposal,
            #         review=review,
            #         config=self.config,
            #     )
            #     self.rebuttals.append(rebuttal)
            #     yield rebuttal, self.leader

            # Paper Meta Reviewing
            scores = [review.score for review in self.reviews]
            metareview = self.chair.write_metareview(
                proposal=proposal,
                reviews=self.reviews,
                config=self.config,
                scores=scores,
            )
            self.metareviews.append(metareview)
            yield metareview, self.chair

        return None
