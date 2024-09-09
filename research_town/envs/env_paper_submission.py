from collections import Counter

from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    IdeaBrainstormingLog,
    LiteratureReviewLog,
    ProposalWritingLog,
    Researcher,
    LogDB,
    PaperDB,
    ProgressDB,
    Idea,
)
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


class PaperSubmissionEnv(BaseEnv):
    def __init__(
        self,
        env_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        config: Config,
    ) -> None:
        super().__init__(
            env_db=env_db,
            progress_db=progress_db,
            paper_db=paper_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        stop_flag: bool,
        agent_profiles: List[Researcher],
        agent_roles: List[Role],
        agent_models: List[str],
        *args: Any,
        **kwargs: Any,
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
    def on_exit(self) -> bool:
        if self.stop_flag:
            raise NotImplementedError('Stop signal is not implemented yet.')
        for insight in self.insights:
            self.progress_db.add(insight)
        for idea in self.ideas:
            self.progress_db.add(idea)
        self.progress_db.add(self.paper)
        self.env_run_num += 1
        return True

    @beartype
    def run(
        self,
    ) -> None:
        # TODO: support retrieval from database
        available_papers = list(self.paper_db.data.values())
        related_papers = self.paper_db.match(
            query=self.proj_leader.profile.bio,
            paper_profiles=available_papers,
            num=2,
        )

        # leader review literature
        self.insights = self.proj_leader.review_literature(
            papers=related_papers,
            domains=['machine learning'],
            config=self.config,
        )
        for insight in self.insights:
            self.progress_db.add(insight)
        self.env_db.add(
            LiteratureReviewLog(
                time_step=self.time_step,
                paper_pks=[paper.pk for paper in related_papers],
                agent_pk=self.proj_leader.profile.pk,
                insight_pks=[insight.pk for insight in self.insights],
            )
        )

        # leader brainstorm idea
        self.ideas: List[Idea] = []
        idea = self.proj_leader.brainstorm_idea(
            insights=self.insights, config=self.config
        )
        self.ideas.append(idea)
        self.progress_db.add(idea)
        self.env_db.add(
            IdeaBrainstormingLog(
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
                IdeaBrainstormingLog(
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
        self.paper = self.proj_leader.write_proposal(
            idea=summarized_idea, papers=related_papers, config=self.config
        )
        self.progress_db.add(self.paper)
        self.env_db.add(
            ProposalWritingLog(
                time_step=self.time_step,
                paper_pk=self.paper.pk,
                agent_pk=self.proj_leader.profile.pk,
            )
        )
