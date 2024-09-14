from typing import List

from ..configs import Config
from ..dbs import Profile, ProfileDB, Proposal
from .agent import Agent


class AgentManager:
    def __init__(self, config: Config, profile_db: ProfileDB) -> None:
        self.config = config
        self.profile_db = profile_db

    def create_leader(self, leader_profile: Profile) -> Agent:
        return Agent(
            agent_profile=leader_profile,
            agent_role='leader',
            model_name=self.config.param.base_llm,
        )

    def create_member(self, member_profile: Profile) -> Agent:
        return Agent(
            agent_profile=member_profile,
            agent_role='member',
            model_name=self.config.param.base_llm,
        )

    def create_chair(self, chair_profile: Profile) -> Agent:
        return Agent(
            agent_profile=chair_profile,
            agent_role='chair',
            model_name=self.config.param.base_llm,
        )

    def create_reviewer(self, reviewer_profile: Profile) -> Agent:
        return Agent(
            agent_profile=reviewer_profile,
            agent_role='reviewer',
            model_name=self.config.param.base_llm,
        )

    def find_members(self, profile: Profile) -> List[Agent]:
        member_profiles = self.profile_db.match_member_profiles(
            leader=profile,
            member_num=self.config.param.member_num,
        )
        return [
            self.create_member(member_profile) for member_profile in member_profiles
        ]

    def find_reviewers(self, proposal: Proposal) -> List[Agent]:
        reviewer_profiles = self.profile_db.match_reviewer_profiles(
            proposal=proposal,
            reviewer_num=self.config.param.reviewer_num,
        )
        return [
            self.create_reviewer(reviewer_profile)
            for reviewer_profile in reviewer_profiles
        ]

    def find_chair(self, proposal: Proposal) -> Agent:
        chair_profile = self.profile_db.match_chair_profiles(
            proposal=proposal,
            chair_num=1,
        )[0]
        return self.create_chair(chair_profile)

    def find_leader(self, task: str) -> Agent:
        leader_profile = self.profile_db.match_leader_profiles(
            query=task, leader_num=1
        )[0]
        return self.create_leader(leader_profile)
