from beartype import beartype
from beartype.typing import Dict, List, Tuple

from ..dbs import (
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
)
from .env_base import BaseMultiAgentEnv


class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
    ) -> None:
        super().__init__(agent_profiles)
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.decision = 'reject'
        self.submission = PaperProfile()
        self.reviewer_mask = [False] * len(agent_profiles)
        self.reviews: List[AgentPaperReviewLog] = []
        self.rebuttals: List[AgentPaperRebuttalLog] = []
        self.meta_reviews: List[AgentPaperMetaReviewLog] = []
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db

    @beartype
    def assign_roles(self, role_dict: Dict[str, str] | None) -> None:
        if role_dict is not None:
            for index, agent_profile in enumerate(self.agent_profiles):
                if role_dict[agent_profile.pk] == 'reviewer':
                    self.reviewer_mask[index] = True
        else:
            pass

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

    def step(self) -> None:
        # Paper Reviewing
        for index, agent in enumerate(self.agents):
            if self.reviewer_mask[index]:
                self.reviews.append(
                    agent.write_paper_review(paper=self.submission))

        # Paper Meta Reviewing
        for index, agent in enumerate(self.agents):
            if self.reviewer_mask[index]:
                self.meta_reviews.append(
                    agent.write_paper_meta_review(
                        paper=self.submission, reviews=self.reviews
                    )
                )

        # Rebuttal Submitting
        for index, agent in enumerate(self.agents):
            for review in self.reviews:
                if self.reviewer_mask[index]:
                    self.rebuttals.append(
                        agent.write_rebuttal(
                            paper=self.submission,
                            review=review,
                        )
                    )

        self.turn_number += 1
        if self.turn_number >= self.turn_max:
            self.terminated = True
