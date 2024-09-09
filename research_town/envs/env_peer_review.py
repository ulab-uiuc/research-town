from collections import Counter

from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    MetaReviewWritingLog,
    RebuttalWritingLog,
    ReviewWritingLog,
    Researcher,
    LogDB,
    PaperDB,
    ProgressDB,
    ResearchRebuttal,
    Review,
)
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class PeerReviewEnv(BaseEnv):
    def __init__(
        self,
        env_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        config: Config,
    ) -> None:
        super().__init__(
            env_db=env_db,
            progress_db=progress_db,
            paper_db=paper_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: List[Researcher],
        agent_roles: List[Role],
        agent_models: List[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.time_step = time_step
        self.stop_flag = stop_flag
        self.paper = kwargs['paper']

        assert len(agent_profiles) == len(agent_roles)

        for agent_profile, agent_role, agent_model in zip(
            agent_profiles, agent_roles, agent_models
        ):
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    agent_role=agent_role,
                    model_name=agent_model,
                )
            )

        if 'proj_leader' not in agent_roles:
            raise ValueError('At least one proj_leader is required to write rebuttal.')
        if 'reviewer' not in agent_roles:
            raise ValueError('At least one reviewer is required to write review.')
        if 'chair' not in agent_roles:
            raise ValueError('At least one chair is required to write meta-review.')
        if 'proj_participant' in agent_roles:
            raise ValueError('Proj_participant role is not allowed in peer review.')

        counter = Counter(agent_roles)
        if counter['proj_leader'] != 1:
            raise ValueError('Exactly one proj_leader is required to write rebuttal.')
        if counter['chair'] != 1:
            raise ValueError('Exactly one chair is required to write meta-review.')

        self.chair = [agent for agent in self.agents if agent.role == 'chair'][0]
        self.proj_leader = [
            agent for agent in self.agents if agent.role == 'proj_leader'
        ][0]
        self.reviewers = [agent for agent in self.agents if agent.role == 'reviewer']

    @beartype
    def on_exit(self) -> bool:
        if self.stop_flag:
            raise NotImplementedError('Stop signal is not implemented yet.')
        self.progress_db.add(self.meta_review)
        for rebuttal in self.rebuttals:
            self.progress_db.add(rebuttal)
        for review in self.reviews:
            self.progress_db.add(review)
        self.env_run_num += 1
        return True

    @beartype
    def run(self) -> None:
        # Paper Reviewing
        self.reviews: List[Review] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper=self.paper,
                config=self.config,
            )
            self.reviews.append(review)
            self.progress_db.add(review)
            self.env_db.add(
                ReviewWritingLog(
                    time_step=self.time_step,
                    agent_pk=reviewer.profile.pk,
                    paper_pk=self.paper.pk,
                )
            )

        # Rebuttal Submitting
        self.rebuttals: List[ResearchRebuttal] = []
        for review in self.reviews:
            rebuttal = self.proj_leader.write_rebuttal(
                paper=self.paper,
                review=review,
                config=self.config,
            )
            self.rebuttals.append(rebuttal)
            self.progress_db.add(rebuttal)
            self.env_db.add(
                RebuttalWritingLog(
                    time_step=self.time_step,
                    paper_pk=rebuttal.paper_pk,
                    agent_pk=self.proj_leader.profile.pk,
                    rebuttal_content=rebuttal.content,
                )
            )

        # Paper Meta Reviewing
        self.meta_review = self.chair.write_meta_review(
            paper=self.paper,
            reviews=self.reviews,
            rebuttals=self.rebuttals,
            config=self.config,
        )
        self.progress_db.add(self.meta_review)
        self.env_db.add(
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
