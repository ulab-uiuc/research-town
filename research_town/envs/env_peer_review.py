from collections import Counter

from beartype import beartype
from beartype.typing import Dict, List, Literal, Tuple, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    AgentPaperMetaReviewWritingLog,
    AgentPaperRebuttalWritingLog,
    AgentPaperReviewWritingLog,
    AgentProfile,
    EnvLogDB,
    ProgressDB,
    ResearchMetaReviewForPaperSubmission,
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
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        config: Config,
    ) -> None:
        super().__init__(agent_profiles=agent_profiles, agent_roles=agent_roles)
        self.chair, self.proj_leader, self.reviewers = self.on_enter(
            agent_profiles=agent_profiles, agent_roles=agent_roles
        )
        self.env_db = env_db
        self.progress_db = progress_db
        self.config = config

    @beartype
    def on_enter(
        self, agent_profiles: List[AgentProfile], agent_roles: List[Role]
    ) -> Tuple[BaseResearchAgent, BaseResearchAgent, List[BaseResearchAgent]]:
        assert len(agent_profiles) == len(agent_roles)
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

        chair = [agent for agent in self.agents if agent.role == 'chair'][0]
        proj_leader = [agent for agent in self.agents if agent.role == 'proj_leader'][0]
        reviewers = [agent for agent in self.agents if agent.role == 'reviewer']
        return chair, proj_leader, reviewers

    @beartype
    def on_exit(
        self,
        meta_review: ResearchMetaReviewForPaperSubmission,
        rebuttals: List[ResearchRebuttalForPaperSubmission],
        reviews: List[ResearchReviewForPaperSubmission],
    ) -> bool:
        self.progress_db.update(meta_review)
        for rebuttal in rebuttals:
            self.progress_db.update(rebuttal)
        for review in reviews:
            self.progress_db.update(review)
        return True

    @beartype
    def update(
        self,
        paper: ResearchPaperSubmission,
    ) -> Tuple[
        ResearchMetaReviewForPaperSubmission,
        List[ResearchRebuttalForPaperSubmission],
        List[ResearchReviewForPaperSubmission],
    ]:
        # Paper Reviewing
        reviews: List[ResearchReviewForPaperSubmission] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper=paper,
                config=self.config,
            )
            reviews.append(review)
            self.progress_db.add(review)
            self.env_db.add(
                AgentPaperReviewWritingLog(
                    agent_pk=reviewer.profile.pk, paper_pk=paper.pk
                )
            )

        # Rebuttal Submitting
        rebuttals: List[ResearchRebuttalForPaperSubmission] = []
        for review in reviews:
            rebuttal = self.proj_leader.write_rebuttal(
                paper=paper,
                review=review,
                config=self.config,
            )
            rebuttals.append(rebuttal)
            self.progress_db.add(rebuttal)
            self.env_db.add(
                AgentPaperRebuttalWritingLog(
                    paper_pk=rebuttal.paper_pk,
                    agent_pk=self.proj_leader.profile.pk,
                    rebuttal_content=rebuttal.content,
                )
            )

        # Paper Meta Reviewing
        meta_review = self.chair.write_meta_review(
            paper=paper,
            reviews=reviews,
            rebuttals=rebuttals,
            config=self.config,
        )
        self.progress_db.add(meta_review)
        self.env_db.add(
            AgentPaperMetaReviewWritingLog(
                paper_pk=meta_review.paper_pk,
                agent_pk=self.chair.profile.pk,
                summary=meta_review.summary,
                strength=meta_review.strength,
                weakness=meta_review.weakness,
                decision=meta_review.decision,
            )
        )

        self.env_run_number += 1
        self.terminated = True

        return meta_review, rebuttals, reviews
