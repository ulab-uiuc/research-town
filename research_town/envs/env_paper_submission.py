from beartype import beartype
from beartype.typing import Dict, Generator, List, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
    ResearchPaperSubmission,
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        config: Config,
        task: Dict[str, str],
    ) -> None:
        super().__init__(agent_profiles)
        self.task = task
        self.paper = PaperProfile()
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db
        self.config = config

    def next_step(
        self,
    ) -> Generator[LogType, None, None]:
        # TODO: support retrieval from database
        # external_data = self.db.get(cls=PaperProfile, conditions={})
        papers = list(self.paper_db.data.values())
        submissions: Dict[str, ResearchPaperSubmission] = {}
        # self.agents=self.agents[:2]
        for lead_agent in self.agents:
            insights = lead_agent.read_paper(
                papers=papers, domains=['machine learning'],config=self.config
            )

            # TODO: this part of logic is wrong, we cannot write paper based on multiple ideas

            ideas = [lead_agent.think_idea(insights=insights,config=self.config)]

            previous_collaborator_profiles = []
            for agent_profile in self.agent_profiles:
                if agent_profile.name in lead_agent.profile.collaborators:
                    previous_collaborator_profiles.append(agent_profile)

            collaborator_pks = self.agent_db.match(
                idea=ideas[0].content, agent_profiles=previous_collaborator_profiles, num=1
            )

            for agent in self.agents:
                if agent.profile.pk in collaborator_pks:
                    ideas.append(agent.think_idea(insights=insights,config=self.config))
            author_pks=collaborator_pks.copy()
            author_pks.append(lead_agent.profile.pk)
            paper = lead_agent.write_paper(ideas, papers,self.config)
            paper.authors=author_pks
            paper.insight=insights[0].content
            # TODO: this is not correct, we cannot write PaperProfile, we can only write PaperSubmission

            if lead_agent.profile.name is not None:
                submissions[lead_agent.profile.name] = paper

        self.db.update(cls=PaperProfile, conditions={}, updates=submissions)
        self.submit_paper(submissions)
        self.terminated = True

    @beartype
    def submit_paper(self, paper_dict: Dict[str, ResearchPaperSubmission]) -> None:
        self.paper = paper_dict