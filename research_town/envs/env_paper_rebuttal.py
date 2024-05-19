from typing import Dict

from .env_base import BaseMultiAgentEnv


class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        super().__init__(agent_dict)
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.roles: Dict[str, str] = {}
        self.submission: Dict[str, str] = {}
        self.review = ""
        self.decision = ""
        self.rebuttal = ""

    def assign_roles(self, role_dict: Dict[str, str]) -> None:
        self.roles = role_dict

    def initialize_submission(self, external_data: Dict[str, str]) -> None:
        self.submission = external_data

    def submit_review(self, review_dict: Dict[str, str]) -> None:
        review_serialize = [
            f"Reviewer: {name}\nReview: {review}" for name, review in review_dict.items()]
        self.review = "\n\n".join(review_serialize)

    def submit_decision(self, decision_dict: Dict[str, str]) -> None:
        decision_count = {"accept": 0, "reject": 0}
        for _, decision in decision_dict.items():
            decision_count[decision] += 1
        count_max = 0
        for decision, count in decision_count.items():
            if count > count_max:
                count_max = count
                self.decision = decision

    def submit_rebuttal(self, rebuttal_dict: Dict[str, str]) -> None:
        rebuttal_serialize = [
            f"Author: {name}\nRebuttal: {rebuttal}" for name, rebuttal in rebuttal_dict.items()]
        self.rebuttal = "\n\n".join(rebuttal_serialize)

    def step(self) -> None:
        # Paper Reviewing
        review_dict: Dict[str, str] = {}
        for name, role in self.roles.items():
            if role == "reviewer":
                review_dict[name] = self.agents[name].review_paper(
                    external_data=self.submission)
        self.submit_review(review_dict)

        # Decision Making
        decision_dict: Dict[str, str] = {}
        for name, role in self.roles.items():
            if role == "reviewer":
                decision_dict[name] = self.agents[name].make_review_decision(
                    submission=self.submission, review=review_dict)
        self.submit_decision(decision_dict)

        # Rebuttal Submitting
        rebuttal_dict: Dict[str, str] = {}
        for name, role in self.roles.items():
            if role == "author":
                rebuttal_dict[name] = self.agents[name].rebut_review(
                    submission=self.submission,
                    review=review_dict,
                    decision=decision_dict)
        self.submit_rebuttal(rebuttal_dict)

        self.turn_number += 1
        if self.decision == "accept":
            self.terminated = True
        if self.turn_number >= self.turn_max:
            self.terminated = True
