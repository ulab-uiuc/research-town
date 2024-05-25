from typing import Dict, List, Tuple

from ..dbs import (
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
    AgentProfile,
    PaperProfile,
)
from .env_base import BaseMultiAgentEnv


class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(self, agent_profiles: List[AgentProfile]) -> None:
        super().__init__(agent_profiles)
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.decision = "reject"
        self.submission = PaperProfile()
        self.reviewer_mask = [False] * len(agent_profiles)
        self.review: List[AgentPaperReviewLog] = []
        self.rebuttal: List[AgentPaperRebuttalLog] = []
        self.meta_review: List[AgentPaperMetaReviewLog] = []

    def assign_roles(self, role_dict: Dict[str, str]) -> None:
        for index, agent_profile in enumerate(self.agent_profiles):
            if role_dict[agent_profile.pk] == "reviewer":
                self.reviewer_mask[index] = True

    def initialize_submission(self, paper_profile: PaperProfile) -> None:
        self.submission = paper_profile

    def submit_decision(self, decision_dict: Dict[str, Tuple[bool, str]]) -> None:
        decision_count = {"accept": 0, "reject": 0}
        for _, decision in decision_dict.items():
            if decision[0]:
                decision_count["accept"] += 1
            else:
                decision_count["reject"] += 1
        count_max = 0
        for d, count in decision_count.items():
            if count > count_max:
                count_max = count
                self.decision = d

    def step(self) -> None:
        # Paper Reviewing
        for index, agent in enumerate(self.agents):
            if self.reviewer_mask[index]:
                self.review.append(agent.review_paper(
                    paper=self.submission))

        # Paper Meta Reviewing
        for index, agent in enumerate(self.agents):
            if self.reviewer_mask[index]:
                self.meta_review.append(agent.make_review_decision(
                    paper=self.submission, review=self.review))

        # Rebuttal Submitting
        for index, agent in enumerate(self.agents):
            if self.reviewer_mask[index]:
                self.rebuttal.append(agent.rebut_review(
                    paper=self.submission,
                    review=self.review,
                    decision=self.meta_review))

        self.turn_number += 1
        if self.turn_number >= self.turn_max:
            self.terminated = True
