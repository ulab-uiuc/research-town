from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Tuple, Union

from ..agents.agent_base import ResearchAgent
from ..configs import Config
from ..dbs import LogDB, PaperDB, Profile, ProfileDB, ProgressDB, Rebuttal, Review
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
        self.leader = ResearchAgent(
            agent_profile=leader_profile,
            agent_role='leader',
            model_name=self.config.param.base_llm,
        )

        chair_profile = self.profile_db.match_chair_profiles(
            proposal=self.proposal,
            chair_num=1,
        )[0]
        self.chair = ResearchAgent(
            agent_profile=chair_profile,
            agent_role='chair',
            model_name=self.config.param.base_llm,
        )

        reviewer_profiles = self.profile_db.match_reviewer_profiles(
            proposal=self.proposal,
            reviewer_num=self.config.param.reviewer_num,
        )
        self.reviewers = [
            ResearchAgent(
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
    def run(self) -> Tuple[Any, Profile]:
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
