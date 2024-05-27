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
        task: Dict[str, str]
    ) -> None:
        super().__init__(agent_profiles)
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.task = task
        self.paper = PaperProfile()
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db

    def step(self) -> None:
        # TODO: support retrieval from database
        # external_data = self.db.get(cls=PaperProfile, conditions={})
        external_data = [PaperProfile(title="A Survey on Machine Learning",
                                      abstract="This paper surveys the field of machine learning."), PaperProfile(title="A Survey on Natural Language Processing", abstract="This paper surveys the field of natural language processing.")]
        agent_names_to_objs: Dict[str, BaseResearchAgent] = {}
        for iter_agent in self.agents:
            if iter_agent.profile.name is not None:
                agent_names_to_objs[iter_agent.profile.name] = iter_agent
        abstracts: Dict[str, PaperProfile] = {}
        for agent in self.agents:
            # TODO: update find collaborator functions with initial task
            collaborators = agent.find_collaborators(PaperProfile(title="A Survey on Machine Learning",
                                                                  abstract="This paper surveys the field of machine learning."))
            # collaborators = [AgentProfile(
            #     name="Rex Ying", bio="Machine Learing Researcher.")]
            collaborator_agents: List[BaseResearchAgent] = []
            for researcher_profile in collaborators:
                if researcher_profile.name:
                    if researcher_profile.name not in agent_names_to_objs:
                        new_agent_obj = BaseResearchAgent(researcher_profile)
                        collaborator_agents.append(new_agent_obj)
                        agent_names_to_objs[researcher_profile.name] = new_agent_obj
                    else:
                        collaborator_agents.append(
                            agent_names_to_objs[researcher_profile.name])

            ideas = agent.generate_idea(
                papers=external_data, domain="machine learning")
            for collaborator_agent in collaborator_agents:
                ideas.extend(collaborator_agent.generate_idea(
                    papers=external_data, domain="machine learning"))
            abstract = agent.write_paper(ideas, external_data)
            if agent.profile.name is not None:
                abstracts[agent.profile.name] = abstract
        self.db.update(cls=PaperProfile, conditions={}, updates=abstracts)
        self.submit_paper(abstracts)
        self.terminated = True

    def submit_paper(self, paper_dict: Dict[str, PaperProfile]) -> None:
        # TODO: clarify paper submission
        for _, paper in paper_dict.items():
            self.paper = paper
            break
