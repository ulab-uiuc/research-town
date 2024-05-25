from typing import Dict, List

from ..agents.agent_base import BaseResearchAgent
from .env_base import BaseMultiAgentEnv
from ..dbs import AgentProfile, EnvLogDB, PaperProfile, PaperProfileDB, AgentProfileDB


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(
        self, 
        agent_profiles: List[AgentProfile], 
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        task: Dict[str, str]
    ) -> None:
        super(PaperSubmissionMultiAgentEnvironment, self).__init__(agent_profiles)
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.paper = ""
        self.task = task
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db

    def step(self) -> None:
        papers = self.paper_db.get_data("machine learning")
        agent_names_to_objs = {
            self.agents[iter_agent].name: self.agents[iter_agent]
            for iter_agent in self.agents
        }  # map from real names to agent objects
        abstracts = {}
        for agent_name, agent in self.agents.items():
            trend = agent.read_paper(
                papers=papers, 
                domain="machine learning"
            )
            trends = [trend]
            collaborators = agent.find_collaborators(self.task)
            collaborator_agents = []
            for researcher_name in collaborators:
                if researcher_name not in agent_names_to_objs:
                    new_agent_obj = BaseResearchAgent(researcher_name)
                    collaborator_agents.append(new_agent_obj)
                    agent_names_to_objs[researcher_name] = new_agent_obj
                else:
                    collaborator_agents.append(
                        agent_names_to_objs[researcher_name])
            ideas = agent.generate_idea(
                trends=trends, domain="machine learning")
            for collaborator_agent in collaborator_agents:
                ideas.extend(collaborator_agent.generate_idea(
                    trends=trends, domain="machine learning"))
            abstract = agent.write_paper(ideas, papers)
            abstracts[agent_name] = abstract
        self.kb.update_kb(abstracts)
        self.submit_paper(abstracts)
        self.terminated = True

    def submit_paper(self, paper_dict: Dict[str, str]) -> None:
        paper_serialize = [
            f"Author: {name}\nAbstract: {paper}" for name, paper in paper_dict.items()]
        self.paper = "\n\n".join(paper_serialize)
