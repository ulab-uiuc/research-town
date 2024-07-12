from collections import Counter

from beartype import beartype
from beartype.typing import Dict, List, Literal, Union

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
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class PaperSubmissionMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(
        self,
        env_db: EnvLogDB,
        progress_db: ProgressDB,
        config: Config,
    ) -> None:
        super().__init__(
            env_db=env_db,
            progress_db=progress_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
        agent_models: List[str],
    ) -> None:
        self.time_step = time_step
        self.stop_flag = stop_flag

        assert len(agent_profiles) == len(agent_roles)

        for agent_profile, agent_role, agent_model in zip(
            agent_profiles, agent_roles, agent_models
        ):
            self.agents.append(
                BaseResearchAgent(
                    agent_profile=agent_profile,
                    agent_role=agent_role,
                    model_name=agent_model,
                )
            )

        if 'proj_leader' not in agent_roles:
            raise ValueError('At least one proj_leader is required to submit paper.')
        if 'reviewer' in agent_roles:
            raise ValueError('Reviewer role is not allowed in paper submission.')
        if 'chair' in agent_roles:
            raise ValueError('Chair role is not allowed in paper submission.')

        counter = Counter(agent_roles)
        if counter['proj_leader'] != 1:
            raise ValueError('Exactly one proj_leader is required to submit paper.')

        self.proj_leader = [
            agent for agent in self.agents if agent.role == 'proj_leader'
        ][0]
        self.proj_participants = [
            agent for agent in self.agents if agent.role == 'proj_participant'
        ]

    @beartype
    def on_exit(
        self,
    ) -> bool:
        self.progress_db.update(self.insights)
        self.progress_db.update(self.ideas)
        self.progress_db.update(self.paper)
        self.env_run_num += 1
        return True

    @beartype
    def update(
        self,
    ) -> None:
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
        self.insights = self.proj_leader.review_literature(
            papers=papers,
            domains=['machine learning'],
            config=self.config,
        )
        for insight in self.insights:
            self.progress_db.add(self.insight)
        self.env_db.add(
            AgentPaperLiteratureReviewLog(
                time_step=self.time_step,
                paper_pks=[paper.pk for paper in papers],
                agent_pk=self.proj_leader.profile.pk,
                insight_pks=[insight.pk for insight in self.insights],
            )
        )

        # leader brainstorm idea
        self.ideas: List[ResearchIdea] = []
        idea = self.proj_leader.brainstorm_idea(
            insights=self.insights, config=self.config
        )
        self.ideas.append(idea)
        self.progress_db.add(idea)
        self.env_db.add(
            AgentIdeaBrainstormingLog(
                time_step=self.time_step,
                idea_pk=idea.pk,
                agent_pk=self.proj_leader.profile.pk,
            )
        )

        # collaborator brainstorm idea
        for participant in self.proj_participants:
            idea = participant.brainstorm_idea(
                insights=self.insights, config=self.config
            )
            self.ideas.append(idea)
            self.progress_db.add(idea)
            self.env_db.add(
                AgentIdeaBrainstormingLog(
                    time_step=self.time_step,
                    idea_pk=idea.pk,
                    agent_pk=participant.profile.pk,
                )
            )

        # leader discuss idea
        summarized_idea = self.proj_leader.discuss_idea(
            ideas=self.ideas, config=self.config
        )
        self.progress_db.add(summarized_idea)

        # write paper
        self.paper = self.proj_leader.write_paper(
            idea=summarized_idea, papers=papers, config=self.config
        )
        self.progress_db.add(self.paper)
        self.env_db.add(
            AgentPaperWritingLog(
                time_step=self.time_step,
                paper_pk=self.paper.pk,
                agent_pk=self.proj_leader.profile.pk,
            )
        )
