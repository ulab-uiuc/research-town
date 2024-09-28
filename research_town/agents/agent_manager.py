from typing import List, Optional

from ..configs import Config
from ..dbs import Profile, ProfileDB, Proposal
from .agent import Agent


class AgentManager:
    def __init__(self, config: Config, profile_db: ProfileDB) -> None:
        self.config = config
        self.profile_db = profile_db

    def create_agent(self, profile: Profile, role: str) -> Agent:
        return Agent(
            agent_profile=profile,
            agent_role=role,
            model_name=self.config.param.base_llm,
        )

    def find_profiles(
        self,
        role: str,
        query: Optional[str] = None,
        proposal: Optional[Proposal] = None,
        mode: str = 'retrieval',
        num: int = 1,
    ) -> List[Profile]:
        """Generalized method to find profiles based on role and mode ('retrieval' or 'sample')."""
        find_methods = {
            'leader': {
                'retrieval': lambda: self.profile_db.match_leader_profiles(
                    query, leader_num=num
                ),
                'sample': lambda: self.profile_db.sample_leader_profiles(
                    leader_num=num
                ),
            },
            'member': {
                'retrieval': lambda: self.profile_db.match_member_profiles(
                    leader=query, member_num=num
                ),
                'sample': lambda: self.profile_db.sample_member_profiles(
                    member_num=num
                ),
            },
            'reviewer': {
                'retrieval': lambda: self.profile_db.match_reviewer_profiles(
                    proposal, reviewer_num=num
                ),
                'sample': lambda: self.profile_db.sample_reviewer_profiles(
                    reviewer_num=num
                ),
            },
            'chair': {
                'retrieval': lambda: self.profile_db.match_chair_profiles(
                    proposal, chair_num=num
                ),
                'sample': lambda: self.profile_db.sample_chair_profiles(chair_num=num),
            },
        }

        return find_methods.get(role, {}).get(mode, lambda: [])()

    def find_members(self, profile: Profile, mode: str = 'sample') -> List[Agent]:
        member_profiles = self.find_profiles(
            role='member',
            query=profile,
            mode=mode,
            num=self.config.param.member_num,
        )
        return [
            self.create_agent(member_profile, 'member')
            for member_profile in member_profiles
        ]

    def find_reviewers(
        self, proposal: Proposal, mode: str = 'sample'
    ) -> List[Agent]:
        reviewer_profiles = self.find_profiles(
            role='reviewer',
            proposal=proposal,
            mode=mode,
            num=self.config.param.reviewer_num,
        )
        return [
            self.create_agent(reviewer_profile, 'reviewer')
            for reviewer_profile in reviewer_profiles
        ]

    def find_chair(self, proposal: Proposal, mode: str = 'sample') -> Agent:
        chair_profile = self.find_profiles(
            role='chair',
            proposal=proposal,
            mode=mode,
            num=1,
        )[0]
        return self.create_agent(chair_profile, 'chair')

    def find_leader(self, task: str, mode: str = 'sample') -> Agent:
        leader_profile = self.find_profiles(
            role='leader',
            query=task,
            mode=mode,
            num=1,
        )[0]
        return self.create_agent(leader_profile, 'leader')
