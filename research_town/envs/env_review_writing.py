from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    LogDB,
    MetaReviewWritingLog,
    PaperDB,
    ProfileDB,
    ProgressDB,
    Rebuttal,
    RebuttalWritingLog,
    Review,
    ReviewWritingLog,
)
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
        profile_db: ProfileDB,
        config: Config,
    ) -> None:
        super().__init__(
            name=name,
            log_db=log_db,
            progress_db=progress_db,
            paper_db=paper_db,
            profile_db=profile_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.time_step = time_step
        self.proposal = kwargs['proposal']

        leader_profile = kwargs['leader_profile']
        self.leader = BaseResearchAgent(
            agent_profile=leader_profile,
            agent_role='leader',
            model_name=self.config.param.base_llm,
        )

        chair_profile = self.profile_db.invite_chair_profiles(
            proposal=self.proposal,
            chair_num=1,
        )[0]
        self.chair = BaseResearchAgent(
            agent_profile=chair_profile,
            agent_role='chair',
            model_name=self.config.param.base_llm,
        )

        reviewer_profiles = self.profile_db.invite_reviewer_profiles(
            proposal=self.proposal,
            reviewer_num=self.config.param.reviewer_num,
        )
        self.reviewers = [
            BaseResearchAgent(
                agent_profile=reviewer_profile,
                agent_role='reviewer',
                model_name=self.config.param.base_llm,
            )
            for reviewer_profile in reviewer_profiles
        ]

    @beartype
    def on_exit(self) -> str:
        self.env_run_num += 1
        return 'proposal_accept'

    @beartype
    def run(self) -> None:
        self.reviews: List[Review] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper=self.proposal,
                config=self.config,
            )
            self.reviews.append(review)
            self.progress_db.add(review)
            self.log_db.add(
                ReviewWritingLog(
                    time_step=self.time_step,
                    agent_pk=reviewer.profile.pk,
                    paper_pk=self.proposal.pk,
                )
            )

        # Rebuttal Submitting
        self.rebuttals: List[Rebuttal] = []
        for review in self.reviews:
            rebuttal = self.leader.write_rebuttal(
                paper=self.proposal,
                review=review,
                config=self.config,
            )
            self.rebuttals.append(rebuttal)
            self.progress_db.add(rebuttal)
            self.log_db.add(
                RebuttalWritingLog(
                    time_step=self.time_step,
                    paper_pk=rebuttal.paper_pk,
                    agent_pk=self.leader.profile.pk,
                    rebuttal_content=rebuttal.content,
                )
            )

        # Paper Meta Reviewing
        self.meta_review = self.chair.write_meta_review(
            paper=self.proposal,
            reviews=self.reviews,
            rebuttals=self.rebuttals,
            config=self.config,
        )
        self.progress_db.add(self.meta_review)
        self.log_db.add(
            MetaReviewWritingLog(
                time_step=self.time_step,
                paper_pk=self.meta_review.paper_pk,
                agent_pk=self.chair.profile.pk,
                summary=self.meta_review.summary,
                strength=self.meta_review.strength,
                weakness=self.meta_review.weakness,
                decision=self.meta_review.decision,
            )
        )
