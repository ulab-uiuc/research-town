from beartype import beartype
from beartype.typing import Dict, List, Literal, Tuple, Union

from ..configs import Config
from ..dbs import (
    AgentPaperMetaReviewWritingLog,
    AgentPaperRebuttalWritingLog,
    AgentPaperReviewWritingLog,
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
    ProgressDB,
    ResearchMetaReviewForPaperSubmission,
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
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        config: Config,
    ) -> None:
        agent_profiles, agent_roles = self.filter_agents(
            agent_profiles=agent_profiles, agent_roles=agent_roles
        )
        super().__init__(agent_profiles=agent_profiles, agent_roles=agent_roles)
        self.decision = 'reject'
        self.submission = PaperProfile()
        self.reviewer_mask = [False] * len(agent_profiles)
        self.reviews: List[ResearchReviewForPaperSubmission] = []
        self.rebuttals: List[ResearchRebuttalForPaperSubmission] = []
        self.meta_reviews: List[ResearchMetaReviewForPaperSubmission] = []
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db
        self.progress_db = progress_db
        self.config = config

    @beartype
    def filter_agents(
        self, agent_profiles: List[AgentProfile], agent_roles: List[Role]
    ) -> Tuple[List[AgentProfile], List[Role]]:
        assert len(agent_profiles) == len(agent_roles)
        if 'proj_leader' not in agent_roles:
            raise ValueError('At least one proj_leader is required to write rebuttal.')
        if 'reviewer' not in agent_roles:
            raise ValueError('At least one reviewer is required to write review.')
        if 'chair' not in agent_roles:
            raise ValueError('At least one chair is required to write meta-review.')

        valid_agent_profiles: List[AgentProfile] = []
        valid_agent_roles: List[Role] = []
        for profile, role in zip(agent_profiles, agent_roles):
            if role == 'reviewer' or role == 'chair' or role == 'proj_leader':
                valid_agent_profiles.append(profile)
                valid_agent_roles.append(role)
        return valid_agent_profiles, valid_agent_roles

    @beartype
    def initialize_submission(self, paper_profile: PaperProfile) -> None:
        self.submission = paper_profile

    @beartype
    def submit_decision(self, decision_dict: Dict[str, Tuple[bool, str]]) -> None:
        decision_count = {'accept': 0, 'reject': 0}
        for _, decision in decision_dict.items():
            if decision[0]:
                decision_count['accept'] += 1
            else:
                decision_count['reject'] += 1
        count_max = 0
        for d, count in decision_count.items():
            if count > count_max:
                count_max = count
                self.decision = d

    def step(
        self,
    ) -> None:
        # Paper Reviewing
        for agent in self.agents:
            if agent.role == 'reviewer':
                review = agent.write_paper_review(
                    paper=self.submission,
                    config=self.config,
                )
                self.reviews.append(review)
                self.progress_db.add(review)
                self.env_db.add(
                    AgentPaperReviewWritingLog(
                        agent_pk=agent.profile.pk, paper_pk=self.submission.pk
                    )
                )

        # Rebuttal Submitting
        for agent in self.agents:
            for review in self.reviews:
                if agent.role == 'proj_leader':
                    rebuttal = agent.write_rebuttal(
                        paper=self.submission,
                        review=review,
                        config=self.config,
                    )
                    self.rebuttals.append(rebuttal)
                    # yield from self.log(
                    #     f'Agent {agent.profile.name} gave rebuttal {str(rebuttal)}'
                    # )
                    self.progress_db.add(rebuttal)
                    self.env_db.add(
                        AgentPaperRebuttalWritingLog(
                            paper_pk=rebuttal.paper_pk,
                            agent_pk=agent.profile.pk,
                            rebuttal_content=rebuttal.content,
                        )
                    )

        # Paper Meta Reviewing
        for agent in self.agents:
            if agent.role == 'chair':
                meta_review = agent.write_meta_review(
                    paper=self.submission,
                    reviews=self.reviews,
                    rebuttals=self.rebuttals,
                    config=self.config,
                )
                self.meta_reviews.append(meta_review)
                self.progress_db.add(meta_review)
                self.env_db.add(
                    AgentPaperMetaReviewWritingLog(
                        paper_pk=meta_review.paper_pk,
                        agent_pk=agent.profile.pk,
                        decision=meta_review.decision,
                        meta_review=meta_review.content,
                    )
                )

        self.env_run_number = 1
        self.terminated = True
