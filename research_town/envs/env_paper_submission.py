from typing import List

from ..dbs import AgentProfile, PaperProfile
from .env_base import BaseMultiAgentEnv


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(self, agent_profiles: List[AgentProfile]) -> None:
        super().__init__(agent_profiles)

    def step(self) -> None:
        papers: List[PaperProfile] = self.db.get(
            PaperProfile)  # TODO: add domain="machine learning" and number=10
        for agent in self.agents:
            agent.read_paper(papers=papers, domain="machine learning")
            agent.find_collaborators(paper=papers[0])
            research_ideas: List[str] = agent.generate_idea(
                papers=papers, domain="machine learning")
            agent.write_paper(research_ideas, papers)

        self.submit_paper()

    def submit_paper(self) -> None:
        pass
