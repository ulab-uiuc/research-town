from typing import Any, Dict, List, Literal, Union

from swarm import Agent as SwarmAgent

from ..configs import ParamConfig
from ..data import Paper, Profile, Proposal
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

            def instructions(context_variables: Dict[str, Any]) -> str:
                instructions_str = profile.bio
                papers = context_variables.get('papers', None)

                if papers:
                    seralized_papers = ''
                    for idx, paper in enumerate(papers):
                        assert isinstance(paper, Paper)
                        seralized_papers += f'[{idx + 1}] Title: {paper.title}'
                        authors = ', '.join(paper.authors)
                        seralized_papers += f'Authors: {authors}'
                        seralized_papers += f'Abstract: {paper.abstract}'
                        seralized_papers += f'URL: {paper.url}'
                        seralized_papers += '\n'

                    instructions_str += (
                        f'\n\nYou will refer to the following papers when responding.\n'
                        f'You will use the markdown format [[index]](URL) to refer to the papers.\n'
                        f"Example: 'As mentioned in [[1]](https://arxiv.org/abs/...), the authors ...'\n"
                        f'Here are the papers:\n{seralized_papers}'
                    )

                return instructions_str

            return SwarmAgent(
                name=profile.name,
                instructions=instructions,
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
