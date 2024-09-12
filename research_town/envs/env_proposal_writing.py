from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union

from ..configs import Config
from ..dbs import (
    Idea,
    IdeaBrainstormingLog,
    LiteratureReviewLog,
    LogDB,
    PaperDB,
    ProfileDB,
    ProgressDB,
    ProposalWritingLog,
)
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class ProposalWritingEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        profile_db: ProfileDB,
        config: Config,
    ) -> None:
        super().__init__(
            name=name,
            log_db=log_db,
            progress_db=progress_db,
            paper_db=paper_db,
            profile_db=profile_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        time_step: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.time_step = time_step
        self.leader = kwargs['leader']

        self.members = self.profile_db.search_member_agents(
            leader=self.leader.profile,
            member_num=self.config.param.member_num,
            config=self.config,
        )

    @beartype
    def on_exit(self) -> str:
        self.env_run_num += 1
        return 'start_review'

    @beartype
    def run(self) -> None:
        available_papers = list(self.paper_db.data.values())

        # Each member reviews literature
        self.insights = []
        for agent in self.agents:
            related_papers = self.paper_db.match(
                query=agent.profile.bio,
                paper_profiles=available_papers,
                num=2,
            )
            insights = agent.review_literature(
                papers=related_papers,
                domains=['machine learning'],
                config=self.config,
            )
            self.insights.extend(insights)  # Collect insights from all members
            for insight in insights:
                self.progress_db.add(insight)
            self.log_db.add(
                LiteratureReviewLog(
                    time_step=self.time_step,
                    paper_pks=[paper.pk for paper in related_papers],
                    agent_pk=agent.profile.pk,
                    insight_pks=[insight.pk for insight in insights],
                )
            )

        # Brainstorm ideas
        self.ideas: List[Idea] = []
        for agent in self.agents:
            idea = agent.brainstorm_idea(insights=self.insights, config=self.config)
            self.ideas.append(idea)
            self.progress_db.add(idea)
            self.log_db.add(
                IdeaBrainstormingLog(
                    time_step=self.time_step,
                    idea_pk=idea.pk,
                    agent_pk=agent.profile.pk,
                )
            )

        # Leader discusses ideas
        summarized_idea = self.leader.discuss_idea(ideas=self.ideas, config=self.config)
        self.progress_db.add(summarized_idea)

        # write one proposal
        related_papers = self.paper_db.match(
            query=summarized_idea.content
            if summarized_idea.content
            else self.leader.profile.bio,
            paper_profiles=available_papers,
            num=2,
        )
        self.proposal = self.leader.write_proposal(
            idea=summarized_idea,
            papers=related_papers,
            config=self.config,
        )
        self.progress_db.add(self.proposal)
        self.log_db.add(
            ProposalWritingLog(
                time_step=self.time_step,
                paper_pk=self.proposal.pk,
                agent_pk=self.leader.profile.pk,
            )
        )
