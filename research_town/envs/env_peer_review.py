from collections import Counter

from beartype import beartype
from beartype.typing import Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    AgentPaperMetaReviewWritingLog,
    AgentPaperRebuttalWritingLog,
    AgentPaperReviewWritingLog,
    AgentProfile,
    EnvLogDB,
    ProgressDB,
    ResearchPaperSubmission,
    ResearchRebuttalForPaperSubmission,
    ResearchReviewForPaperSubmission,
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class PeerReviewMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(
        self,
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        config: Config,
    ) -> None:
        super().__init__(
            env_db=env_db,
            progress_db=progress_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
        paper: ResearchPaperSubmission,
    ) -> None:
        self.time_step = time_step
        self.stop_flag = stop_flag
        self.paper = paper

        assert len(agent_profiles) == len(agent_roles)

        for agent_profile, agent_role in zip(agent_profiles, agent_roles):
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    agent_role=agent_role,
                    model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
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
        self.progress_db.update(self.meta_review)
        for rebuttal in self.rebuttals:
            self.progress_db.update(rebuttal)
        for review in self.reviews:
            self.progress_db.update(review)
        return True

    @beartype
    def update(self) -> None:
        # Paper Reviewing
        self.reviews: List[ResearchReviewForPaperSubmission] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper=self.paper,
                config=self.config,
            )
            self.reviews.append(review)
            self.progress_db.add(review)
            self.env_db.add(
                AgentPaperReviewWritingLog(
                    time_step=self.time_step,
                    agent_pk=reviewer.profile.pk,
                    paper_pk=self.paper.pk,
                )
            )

        # Rebuttal Submitting
        self.rebuttals: List[ResearchRebuttalForPaperSubmission] = []
        for review in self.reviews:
            rebuttal = self.proj_leader.write_rebuttal(
                paper=self.paper,
                review=review,
                config=self.config,
            )
            self.rebuttals.append(rebuttal)
            self.progress_db.add(rebuttal)
            self.env_db.add(
                AgentPaperRebuttalWritingLog(
                    time_step=self.time_step,
                    paper_pk=rebuttal.paper_pk,
                    agent_pk=self.proj_leader.profile.pk,
                    rebuttal_content=rebuttal.content,
                )
            )

        # Paper Meta Reviewing
        meta_review = self.chair.write_meta_review(
            paper=self.paper,
            reviews=self.reviews,
            rebuttals=self.rebuttals,
            config=self.config,
        )
        self.progress_db.add(meta_review)
        self.env_db.add(
            AgentPaperMetaReviewWritingLog(
                time_step=self.time_step,
                paper_pk=meta_review.paper_pk,
                agent_pk=self.chair.profile.pk,
                summary=meta_review.summary,
                strength=meta_review.strength,
                weakness=meta_review.weakness,
                decision=meta_review.decision,
            )
        )

        self.env_run_number += 1
