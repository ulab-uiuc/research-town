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
        self.chair = [self.agent_manager.find_chair(proposal) for proposal in self.proposal]
        self.reviewers = [self.agent_manager.find_reviewers(proposal) for proposal in self.proposal]

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
        all_reviews = []
        all_rebuttals = []
        all_metareviews = []

        # Process each proposal in the list
        for i, proposal in enumerate(self.proposal):
            # Review Writing for each proposal
            reviews: List[Review] = []
            for reviewer in self.reviewers[i]:  # Reviewers for the current proposal
                review = reviewer.write_review(
                    paper=proposal,
                    config=self.config,
                )
                reviews.append(review)
                yield review, reviewer

            all_reviews.append(reviews)

            # Rebuttal Submitting for each proposal
            rebuttals: List[Rebuttal] = []
            for review in reviews:
                rebuttal = self.leader.write_rebuttal(
                    paper=proposal,
                    review=review,
                    config=self.config,
                )
                rebuttals.append(rebuttal)
                yield rebuttal, self.leader

            all_rebuttals.append(rebuttals)

            # Meta Reviewing for each proposal
            chair = self.chair[i]  # Chair for the current proposal
            metareview = chair.write_metareview(
                paper=proposal,
                reviews=reviews,
                rebuttals=rebuttals,
                config=self.config,
            )
            yield metareview, chair

            all_metareviews.append(metareview)

        # Store the metareviews as the final result
        self.metareview = all_metareviews

        return None
