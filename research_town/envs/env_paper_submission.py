from typing import Dict, List

from ..agents.agent_base import BaseResearchAgent
from ..dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
)
from .env_base import BaseMultiAgentEnv


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        task: Dict[str, str],
        callback=None
    ) -> None:
        super().__init__(agent_profiles, callback=callback)
        # self.turn_number = 0
        # self.turn_max = 1
        self.terminated = False
        self.task = task
        self.paper = PaperProfile()
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db
        self.state = 0  # State variable to control the step sequence
        self.external_data = []  # Will hold external data once fetched
        self.agent_names_to_objs: Dict[str, BaseResearchAgent] = {}
        self.abstracts: Dict[str, PaperProfile] = {}

    def _step(self) -> None:
        if self.state == 0:
            self.fetch_external_data()
        elif self.state == 1:
            self.initialize_agents()
        elif self.state == 2:
            self.find_collaborators()
        elif self.state == 3:
            self.generate_ideas()
        elif self.state == 4:
            self.write_papers()
        elif self.state == 5:
            self.update_database()
        elif self.state == 6:
            self.submit_papers()
        else:
            self.terminated = True

    def fetch_external_data(self):
        # Simulate data retrieval
        self.external_data = [
            PaperProfile(title="A Survey on Machine Learning",
                         abstract="This paper surveys the field of machine learning."),
            PaperProfile(title="A Survey on Natural Language Processing",
                         abstract="This paper surveys the field of natural language processing.")
        ]
        self.state += 1

    def initialize_agents(self):
        for iter_agent in self.agents:
            if iter_agent.profile.name is not None:
                self.agent_names_to_objs[iter_agent.profile.name] = iter_agent
        self.state += 1

    def find_collaborators(self):
        for agent in self.agents:
            collaborators = agent.find_collaborators(PaperProfile(
                title="A Survey on Machine Learning",
                abstract="This paper surveys the field of machine learning."
            ))
            collaborators = [AgentProfile(name="Rex Ying", bio="Machine Learning Researcher.")]
            collaborator_agents: List[BaseResearchAgent] = []
            for researcher_profile in collaborators:
                if researcher_profile.name:
                    if researcher_profile.name not in self.agent_names_to_objs:
                        new_agent_obj = BaseResearchAgent(researcher_profile)
                        collaborator_agents.append(new_agent_obj)
                        self.agent_names_to_objs[researcher_profile.name] = new_agent_obj
                    else:
                        collaborator_agents.append(
                            self.agent_names_to_objs[researcher_profile.name])
            agent.collaborator_agents = collaborator_agents  # Save collaborators for each agent
        self.state += 1

    def generate_ideas(self):
        for agent in self.agents:
            ideas = agent.generate_idea(
                papers=self.external_data, domain="machine learning")
            for collaborator_agent in agent.collaborator_agents:
                ideas.extend(collaborator_agent.generate_idea(
                    papers=self.external_data, domain="machine learning"))
            agent.ideas = ideas  # Save ideas for each agent
        self.state += 1

    def write_papers(self):
        for agent in self.agents:
            abstract = agent.write_paper(agent.ideas, self.external_data)
            if agent.profile.name is not None:
                self.abstracts[agent.profile.name] = abstract
        self.state += 1

    def update_database(self):
        self.db.update(cls=PaperProfile, conditions={}, updates=self.abstracts)
        self.state += 1

    def submit_papers(self):
        for _, paper in self.abstracts.items():
            self.paper = paper
            break
        self.state += 1
        # self.terminated = True

    def submit_paper(self, paper_dict: Dict[str, PaperProfile]) -> None:
        # TODO: clarify paper submission
        for _, paper in paper_dict.items():
            self.paper = paper
            break
