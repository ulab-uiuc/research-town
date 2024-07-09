from collections import Counter

from beartype import beartype
from beartype.typing import Dict, List, Literal, Tuple, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    AgentIdeaBrainstormingLog,
    AgentPaperLiteratureReviewLog,
    AgentPaperWritingLog,
    AgentProfile,
    EnvLogDB,
    PaperProfile,
    ProgressDB,
    ResearchIdea,
    ResearchPaperSubmission,
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class PaperSubmissionMultiAgentEnvironment(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        config: Config,
    ) -> None:
        super().__init__(agent_profiles=agent_profiles, agent_roles=agent_roles)
        self.env_db = env_db
        self.progress_db = progress_db
        self.config = config
        self.proj_leader, self.proj_participants = self.on_enter(
            agent_profiles=agent_profiles, agent_roles=agent_roles
        )

    @beartype
    def on_enter(
        self, agent_profiles: List[AgentProfile], agent_roles: List[Role]
    ) -> Tuple[BaseResearchAgent, List[BaseResearchAgent]]:
        assert len(agent_profiles) == len(agent_roles)
        if 'proj_leader' not in agent_roles:
            raise ValueError('At least one proj_leader is required to submit paper.')
        if 'reviewer' in agent_roles:
            raise ValueError('Reviewer role is not allowed in paper submission.')
        if 'chair' in agent_roles:
            raise ValueError('Chair role is not allowed in paper submission.')

        counter = Counter(agent_roles)
        if counter['proj_leader'] != 1:
            raise ValueError('Exactly one proj_leader is required to submit paper.')

        proj_leader = [agent for agent in self.agents if agent.role == 'proj_leader'][0]
        proj_participants = [
            agent for agent in self.agents if agent.role == 'proj_participant'
        ]
        return proj_leader, proj_participants

    @beartype
    def on_exit(
        self,
        paper: ResearchPaperSubmission,
    ) -> bool:
        self.progress_db.update(paper)
        return True

    @beartype
    def update(
        self,
    ) -> ResearchPaperSubmission:
        # TODO: support retrieval from database
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

        # TODO: update find collaborator functions with initial task
        # self.proj_participants: List[BaseResearchAgent] = []

        # leader review literature
        insights = self.proj_leader.review_literature(
            papers=papers,
            domains=['machine learning'],
            config=self.config,
        )
        for insight in insights:
            self.progress_db.add(insight)
        self.env_db.add(
            AgentPaperLiteratureReviewLog(
                paper_pks=[paper.pk for paper in papers],
                agent_pk=self.proj_leader.profile.pk,
                insight_pks=[insight.pk for insight in insights],
            )
        )

        # leader brainstorm idea
        ideas: List[ResearchIdea] = []
        idea = self.proj_leader.brainstorm_idea(insights=insights, config=self.config)
        ideas.append(idea)
        self.progress_db.add(idea)
        self.env_db.add(
            AgentIdeaBrainstormingLog(
                idea_pk=idea.pk, agent_pk=self.proj_leader.profile.pk
            )
        )

        # collaborator brainstorm idea
        for participant in self.proj_participants:
            idea = participant.brainstorm_idea(insights=insights, config=self.config)
            ideas.append(idea)
            self.progress_db.add(idea)
            self.env_db.add(
                AgentIdeaBrainstormingLog(
                    idea_pk=idea.pk, agent_pk=participant.profile.pk
                )
            )

        # leader discuss idea
        summarized_idea = self.proj_leader.discuss_idea(ideas=ideas, config=self.config)
        self.progress_db.add(summarized_idea)

        # write paper
        paper = self.proj_leader.write_paper(
            idea=summarized_idea, papers=papers, config=self.config
        )
        self.progress_db.add(paper)
        self.env_db.add(
            AgentPaperWritingLog(
                paper_pk=paper.pk, agent_pk=self.proj_leader.profile.pk
            )
        )

        self.env_run_number += 1
        self.terminated = True

        return paper
