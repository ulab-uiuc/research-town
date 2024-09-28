from typing import List, Literal, Optional

from ..configs import Config
from ..dbs import Profile, ProfileDB, Proposal
from .agent import Agent

Role = Literal['reviewer', 'leader', 'member', 'chair']


class AgentManager:
    def __init__(self, config: Config, profile_db: ProfileDB) -> None:
        self.config = config
        self.profile_db = profile_db

    def create_agent(self, profile: Profile, role: Role) -> Agent:
        return Agent(
            agent_profile=profile,
            agent_role=role,
            model_name=self.config.param.base_llm,
        )

    def find_profiles(
        self,
        role: Role,
        query: Optional[str] = None,
        proposal: Optional[Proposal] = None,
        num: int = 1,
    ) -> List[Profile]:
        """Retrieve profiles based on a query (for leader/member) or a proposal (for reviewer/chair)."""
        find_methods = {
            'leader': lambda: self.profile_db.match_leader_profiles(
                query, leader_num=num
            ),
            'member': lambda: self.profile_db.match_member_profiles(
                leader=query, member_num=num
            ),
            'reviewer': lambda: self.profile_db.match_reviewer_profiles(
                proposal, reviewer_num=num
            ),
            'chair': lambda: self.profile_db.match_chair_profiles(
                proposal, chair_num=num
            ),
        }

        return find_methods.get(role, lambda: [])()

    def sample_profiles(self, role: Role, num: int = 1) -> List[Profile]:
        """Sample profiles for a specific role."""
        sample_methods = {
            'leader': lambda: self.profile_db.sample_leader_profiles(leader_num=num),
            'member': lambda: self.profile_db.sample_member_profiles(member_num=num),
            'reviewer': lambda: self.profile_db.sample_reviewer_profiles(
                reviewer_num=num
            ),
            'chair': lambda: self.profile_db.sample_chair_profiles(chair_num=num),
        }

        return sample_methods.get(role, lambda: [])()

    def find_members(self, profile: Profile) -> List[Agent]:
        member_profiles = self.find_profiles(
            role='member',
            query=profile,
            num=self.config.param.member_num,
        )
        return [
            self.create_agent(member_profile, 'member')
            for member_profile in member_profiles
        ]

    def sample_members(self) -> List[Agent]:
        member_profiles = self.sample_profiles(
            role='member',
            num=self.config.param.member_num,
        )
        return [
            self.create_agent(member_profile, 'member')
            for member_profile in member_profiles
        ]

    def find_reviewers(self, proposal: Proposal) -> List[Agent]:
        reviewer_profiles = self.find_profiles(
            role='reviewer',
            proposal=proposal,
            num=self.config.param.reviewer_num,
        )
        return [
            self.create_agent(reviewer_profile, 'reviewer')
            for reviewer_profile in reviewer_profiles
        ]

    def sample_reviewers(self) -> List[Agent]:
        reviewer_profiles = self.sample_profiles(
            role='reviewer',
            num=self.config.param.reviewer_num,
        )
        return [
            self.create_agent(reviewer_profile, 'reviewer')
            for reviewer_profile in reviewer_profiles
        ]

    def find_chair(self, proposal: Proposal) -> Agent:
        chair_profile = self.find_profiles(
            role='chair',
            proposal=proposal,
            num=1,
        )[0]
        return self.create_agent(chair_profile, 'chair')

    def sample_chair(self) -> Agent:
        chair_profile = self.sample_profiles(
            role='chair',
            num=1,
        )[0]
        return self.create_agent(chair_profile, 'chair')

    def find_leader(self, task: str) -> Agent:
        leader_profile = self.find_profiles(
            role='leader',
            query=task,
            num=1,
        )[0]
        return self.create_agent(leader_profile, 'leader')

    def sample_leader(self) -> Agent:
        leader_profile = self.sample_profiles(
            role='leader',
            num=1,
        )[0]
        return self.create_agent(leader_profile, 'leader')
