from typing import Dict, Tuple

from ..kbs.envlog import (
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
)
from ..kbs.profile import PaperProfile
from .env_base import BaseMultiAgentEnv


class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super().__init__(agent_dict)
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.roles: Dict[str, str] = {}
        self.submission = PaperProfile()
        self.review: Dict[str, AgentPaperReviewLog] = {}
        self.rebuttal: Dict[str, AgentPaperRebuttalLog] = {}
        self.meta_review: Dict[str, AgentPaperMetaReviewLog] = {}
         
    def assign_roles(self, role_dict: Dict[str, str]) -> None:
        self.roles = role_dict

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

    def submit_rebuttal(self, rebuttal_dict: Dict[str, str]) -> None:
        pass

    def step(self) -> None:
        # Paper Reviewing
        for agent_id, role in self.roles.items():
            if role == "reviewer":
                self.review[agent_id] = self.agents[agent_id].review_paper(
                    paper=self.submission)

        # Paper Meta Reviewing
        review_list = [review for _, review in self.review.items()]
        for agent_id, role in self.roles.items():
            if role == "reviewer":
                self.meta_review[agent_id] = self.agents[agent_id].make_review_decision(
                    paper=self.submission, review=review_list)

        # Rebuttal Submitting
        meta_review_list = [meta_review for _, meta_review in self.meta_review.items()]
        for agent_id, role in self.roles.items():
            if role == "author":
                self.rebuttal[agent_id] = self.agents[agent_id].rebut_review(
                    paper=self.submission,
                    review=review_list,
                    decision=meta_review_list)

        self.turn_number += 1
        if self.turn_number >= self.turn_max:
            self.terminated = True
