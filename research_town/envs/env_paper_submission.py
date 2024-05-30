from beartype.typing import Dict, List

from beartype import beartype

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
        papers = [PaperProfile(title="A Survey on Machine Learning",
                                      abstract="This paper surveys the field of machine learning."), PaperProfile(title="A Survey on Natural Language Processing", abstract="This paper surveys the field of natural language processing.")]
        agent_names_to_objs: Dict[str, BaseResearchAgent] = {}
        for iter_agent in self.agents:
            if iter_agent.profile.name is not None:
                agent_names_to_objs[iter_agent.profile.name] = iter_agent
        submissions: Dict[str, PaperProfile] = {}
        for agent in self.agents:
            # TODO: update find collaborator functions with initial task
            collaborators = agent.find_collaborators(PaperProfile(title="A Survey on Machine Learning",
                                                                  abstract="This paper surveys the field of machine learning."))
            collaborator_agents: List[BaseResearchAgent] = []
            for researcher_profile in collaborators:
                if researcher_profile.name:
                    if researcher_profile.name not in agent_names_to_objs:
                        new_agent_obj = BaseResearchAgent(
                            agent_profile=researcher_profile,
                            model_name="together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1"
                        )
                        collaborator_agents.append(new_agent_obj)
                        agent_names_to_objs[researcher_profile.name] = new_agent_obj
                    else:
                        collaborator_agents.append(
                            agent_names_to_objs[researcher_profile.name])

            insights = agent.read_paper(
                papers=papers,
                domains=["machine learning"]
            )
            ideas = agent.think_idea(insights=insights)
            for collaborator_agent in collaborator_agents:
                ideas.extend(collaborator_agent.think_idea(insights=insights))
            paper = agent.write_paper(ideas, papers)

            # TODO: this is not correct, we cannot write PaperProfile, we can only write PaperSubmission
            if agent.profile.name is not None:
                submissions[agent.profile.name] = PaperProfile(abstract=paper.abstract)
        self.db.update(cls=PaperProfile, conditions={}, updates=submissions)
        self.submit_paper(submissions)
        self.terminated = True

    @beartype
    def submit_paper(self, paper_dict: Dict[str, PaperProfile]) -> None:
        # TODO: clarify paper submission
        for _, paper in paper_dict.items():
            self.paper = paper
            break
