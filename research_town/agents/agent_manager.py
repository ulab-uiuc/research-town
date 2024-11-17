from typing import List, Literal, Union

from swarm import Agent as SwarmAgent

from ..configs import ParamConfig
from ..data import Profile, Proposal
from ..dbs import ProfileDB
from .agent import Agent

AgentType = Union[Agent, SwarmAgent]

Role = Literal['reviewer', 'leader', 'member', 'chair']


class AgentManager:
    def __init__(self, config: ParamConfig, profile_db: ProfileDB) -> None:
        self.config = config
        self.profile_db = profile_db
        assert config.mode in ['research_town', 'swarm']
        self.mode = config.mode

    def create_agent(self, profile: Profile, role: Role) -> AgentType:
        if self.mode == 'research_town':
            return Agent(
                profile=profile,
                role=role,
                model_name=self.config.base_llm,
            )
        else:
            return SwarmAgent(
                name=profile.name,
                instructions=profile.bio,
                model=self.config.base_llm,
            )

    def find_agents(self, role: Role, query: str, num: int = 1) -> List[AgentType]:
        profiles = self.profile_db.match(query=query, role=role, num=num)
        return [self.create_agent(profile, role) for profile in profiles]

    def sample_agents(self, role: Role, num: int = 1) -> List[AgentType]:
        profiles = self.profile_db.sample(role=role, num=num)
        return [self.create_agent(profile, role) for profile in profiles]

    # Specific methods for roles
    def find_leader(self, task: str) -> AgentType:
        agents = self.find_agents(role='leader', query=task, num=1)
        assert agents is not None
        return agents[0]

    def sample_leader(self) -> AgentType:
        agents = self.sample_agents(role='leader', num=1)
        assert agents is not None
        return agents[0]

    def find_members(self, leader_profile: Profile) -> List[AgentType]:
        agents = self.find_agents(
            role='member', query=leader_profile.bio, num=self.config.member_num
        )
        return agents

    def sample_members(self) -> List[AgentType]:
        agents = self.sample_agents(role='member', num=self.config.member_num)
        return agents

    def find_reviewers(self, proposal: Proposal) -> List[AgentType]:
        agents = self.find_agents(
            role='reviewer', query=proposal.content, num=self.config.reviewer_num
        )
        return agents

    def sample_reviewers(self) -> List[AgentType]:
        agents = self.sample_agents(role='reviewer', num=self.config.reviewer_num)
        return agents

    def find_chair(self, proposal: Proposal) -> AgentType:
        agents = self.find_agents(role='chair', query=proposal.content, num=1)
        assert agents is not None
        return agents[0]

    def sample_chair(self) -> AgentType:
        agents = self.sample_agents(role='chair', num=1)
        assert agents is not None
        return agents[0]
