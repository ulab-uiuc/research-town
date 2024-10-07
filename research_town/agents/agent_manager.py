from typing import List, Literal

from ..configs import Config
from ..data import Profile, Proposal
from ..dbs import ProfileDB
from .agent import Agent

Role = Literal['reviewer', 'leader', 'member', 'chair']


class AgentManager:
    def __init__(self, config: Config, profile_db: ProfileDB) -> None:
        self.config = config
        self.profile_db = profile_db

    def create_agent(self, profile: Profile, role: Role) -> Agent:
        return Agent(
            profile=profile,
            role=role,
            model_name=self.config.param.base_llm,
        )

    def find_agents(self, role: Role, query: str, num: int = 1) -> List[Agent]:
        profiles = self.profile_db.match(query=query, role=role, num=num)
        return [self.create_agent(profile, role) for profile in profiles]

    def sample_agents(self, role: Role, num: int = 1) -> List[Agent]:
        profiles = self.profile_db.sample(role=role, num=num)
        return [self.create_agent(profile, role) for profile in profiles]

    # Specific methods for roles
    def find_leader(self, task: str) -> Agent:
        agents = self.find_agents(role='leader', query=task, num=1)
        assert agents is not None
        return agents[0]

    def sample_leader(self) -> Agent:
        agents = self.sample_agents(role='leader', num=1)
        assert agents is not None
        return agents[0]

    def find_members(self, leader_profile: Profile) -> List[Agent]:
        agents = self.find_agents(
            role='member', query=leader_profile.bio, num=self.config.param.member_num
        )
        return agents

    def sample_members(self) -> List[Agent]:
        agents = self.sample_agents(role='member', num=self.config.param.member_num)
        return agents

    def find_reviewers(self, proposal: Proposal) -> List[Agent]:
        agents = self.find_agents(
            role='reviewer', query=proposal.content, num=self.config.param.reviewer_num
        )
        return agents

    def sample_reviewers(self) -> List[Agent]:
        agents = self.sample_agents(role='reviewer', num=self.config.param.reviewer_num)
        return agents

    def find_chair(self, proposal: Proposal) -> Agent:
        agents = self.find_agents(role='chair', query=proposal.content, num=1)
        assert agents is not None
        return agents[0]

    def sample_chair(self) -> Agent:
        agents = self.sample_agents(role='chair', num=1)
        assert agents is not None
        return agents[0]
