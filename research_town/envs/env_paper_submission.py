from beartype import beartype
from beartype.typing import Dict, List

from ..dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
    ResearchPaperSubmission,
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
        args: Dict[str, str],
    ) -> None:
        super().__init__(agent_profiles)
        self.turn_number = 0
        self.turn_max = 1
        self.terminated = False
        self.task = task
        self.paper = {}
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db
        self.config_file = args.cfg_file

    def step(self) -> None:
        # TODO: support retrieval from database
        # external_data = self.db.get(cls=PaperProfile, conditions={})
        papers = [
            PaperProfile(
                title='A Survey on Machine Learning',
                abstract='This paper surveys the field of machine learning.',
            ),
            PaperProfile(
                title='A Survey on Natural Language Processing',
                abstract='This paper surveys the field of natural language processing.',
            ),
        ]

        submissions: Dict[str, ResearchPaperSubmission] = {}

        for lead_agent in self.agents:
            insights = lead_agent.read_paper(
                papers=papers, domains=['machine learning']
            )

            # TODO: this part of logic is wrong, we cannot write paper based on multiple ideas

            ideas = [lead_agent.think_idea(insights=insights)]

            previous_collaborator_profiles = []
            for agent_profile in self.agent_profiles:
                if agent_profile.name in lead_agent.profile.collaborators:
                    previous_collaborator_profiles.append(agent_profile)

            collaborator_pks = self.agent_db.match(
                idea=ideas[0], agent_profiles=previous_collaborator_profiles, num=1
            )

            for agent in self.agents:
                if agent.profile.pk in collaborator_pks:
                    ideas.append(agent.think_idea(insights=insights))

            paper = lead_agent.write_paper(ideas, papers)

            # TODO: this is not correct, we cannot write PaperProfile, we can only write PaperSubmission

            if lead_agent.profile.name is not None:
                submissions[lead_agent.profile.name] = paper

        self.db.update(cls=PaperProfile, conditions={}, updates=submissions)
        self.submit_paper(submissions)
        self.terminated = True

    @beartype
    def submit_paper(self, paper_dict: Dict[str, ResearchPaperSubmission]) -> None:
        self.paper = paper_dict
