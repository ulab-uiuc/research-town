from typing import Dict

from beartype.typing import List, Tuple

from ..dbs import (
    AgentProfile,
    AgentProfileDB,
    PaperProfile,
    PaperProfileDB,
    ResearchPaperSubmission,
)
from ..envs.env_base import BaseMultiAgentEnv


class BaseResearchEngine:
    def __init__(self, agent_db: AgentProfileDB, paper_db: PaperProfileDB) -> None:
        self.time_step = 0
        self.envs: Dict[str, BaseMultiAgentEnv] = {}
        self.transition_matrix: Dict[str, Dict[bool, str]] = {}
        self.curr_env_name: str = ''
        self.curr_env: BaseMultiAgentEnv = None
        self.agent_db = agent_db
        self.paper_db = paper_db

    def add_env(self, name: str, env: BaseMultiAgentEnv):
        self.envs[name] = env

    def set_transition(self, from_name: str, pass_name: str, fail_name: str):
        self.transition_matrix[from_name] = {True: pass_name, False: fail_name}

    def set_initial_env(self, name: str):
        self.curr_env_name = name
        self.curr_env = self.envs[name]
        self.curr_env.on_enter()

    def update(self):
        if self.curr_env_name:
            self.curr_env.update()

    def transition(self):
        if self.curr_env:
            result = self.curr_env.on_exit()
            next_env_name = self.transition_matrix[self.curr_env_name][result]
            self.curr_env_name = next_env_name
            self.curr_env = self.envs[next_env_name]
            self.curr_env.on_enter()

    def find_proj_participants(
        self, potential_participants_profiles: List[AgentProfile]
    ) -> List[str]:
        leader_profile = self.leader.bio
        self.proj_participants_pks = self.agent_db.match(
            query=leader_profile, agent_profiles=potential_participants_profiles
        )
        return self.proj_participants_pks

    def find_proj_leaders(self, leader_profile: AgentProfile) -> None:
        self.leader = leader_profile

    def find_reviewers(
        self,
        paper_submission: ResearchPaperSubmission,
        potential_reviewers_profiles: List[AgentProfile],
    ) -> List[str]:
        paper_abstract = paper_submission.abstract
        self.reviewers_pks = self.agent_db.match(
            query=paper_abstract, agent_profiles=potential_reviewers_profiles
        )
        return self.reviewers_pks

    def find_chairs(
        self,
        paper_submission: ResearchPaperSubmission,
        potential_chairs_profiles: List[AgentProfile],
    ) -> Tuple[List[str], List[str]]:
        paper_abstract = paper_submission.abstract
        self.chair_pk = self.agent_db.match(
            query=paper_abstract, agent_profiles=potential_chairs_profiles
        )
        if self.chair_pk in self.reviewers_pks:
            self.other_reviewer_pks = [
                reviewer for reviewer in self.reviewers_pks if reviewer != self.chair_pk
            ]
        else:
            self.other_reviewer_pks = self.reviewers_pks

        return self.chair_pk, self.other_reviewer_pks

    def read_papers(self, potential_paper_profiles: List[PaperProfile]) -> List[str]:
        leader_profile = self.leader.bio
        paper_dks = self.paper_db.match(
            query=leader_profile, paper_profiles=potential_paper_profiles
        )
        return paper_dks

    def recover(self) -> None:
        pass
