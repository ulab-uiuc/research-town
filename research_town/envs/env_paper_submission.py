from beartype import beartype
from beartype.typing import Dict, Generator, List, Union

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
    ) -> None:
        super().__init__(agent_profiles,config)

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
        perform_agents=self.agents[:10]
        for lead_agent in perform_agents:
            insights,related_papers_idx = lead_agent.literature_review(
                papers=papers, domains=[self.config.param.domain],config=self.config
            )
            related_papers=[papers[idx] for idx in related_papers_idx]
            # TODO: this part of logic is wrong, we cannot write paper based on multiple ideas

            ideas = [lead_agent.idea_brainstorming(insights=insights,config=self.config)]

            previous_collaborator_profiles = []
            for agent_profile in self.agent_profiles:
                if agent_profile.name in lead_agent.profile.collaborators:
                    previous_collaborator_profiles.append(agent_profile)
            if len(previous_collaborator_profiles)==0:
                author_pks=[]
            else:
                collaborator_pks = self.agent_db.match(
                    idea=ideas[0].content, agent_profiles=previous_collaborator_profiles, num=self.config.param.max_collaborators_num
                )

                for agent in self.agents:
                    if agent.profile.pk in collaborator_pks:
                        ideas.append(agent.idea_brainstorming(insights=insights,config=self.config))
                author_pks=collaborator_pks.copy()
            author_pks.append(lead_agent.profile.pk)
            paper = lead_agent.paper_abstract_writing(ideas, related_papers,self.config)
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