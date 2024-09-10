from collections import Counter

from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union, Tuple

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    Idea,
    PaperDB,
    ResearcherDB,
    Researcher,
)
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'participant', 'chair'] | None


class ProposalWritingEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        paper_db: PaperDB,
        agent_db: ResearcherDB,
        config: Config,
    ) -> None:
        super().__init__(
            name=name,
            paper_db=paper_db,
            agent_db=agent_db,
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

        if 'leader' not in agent_roles:
            raise ValueError('At least one leader is required to submit paper.')
        if 'reviewer' in agent_roles:
            raise ValueError('Reviewer role is not allowed in paper submission.')
        if 'chair' in agent_roles:
            raise ValueError('Chair role is not allowed in paper submission.')

        counter = Counter(agent_roles)
        if counter['leader'] != 1:
            raise ValueError('Exactly one leader is required to submit paper.')

        self.leader = [
            agent for agent in self.agents if agent.role == 'leader'
        ][0]
        self.participants = [
            agent for agent in self.agents if agent.role == 'participant'
        ]

    @beartype
    def on_exit(self) -> bool:
        return True

    @beartype
    def run(self) -> Tuple[Any, BaseResearchAgent]:
        available_papers = list(self.paper_db.data.values())

        # Each member reviews literature
        self.insights = []
        for agent in self.agents:
            related_papers = self.paper_db.match(
                query=agent.profile.bio,
                paper_profiles=available_papers,
                num=2,
            )
            agent_insights = agent.review_literature(
                papers=related_papers,
                domains=['machine learning'],
                config=self.config,
            )
            yield agent_insights, agent

        # Brainstorm ideas
        self.ideas: List[Idea] = []
        for agent in self.agents:
            idea = agent.bainstorm_idea(
                insights=self.insights, config=self.config
            )
            yield idea, agent

        # Leader discusses ideas
        summarized_idea = self.leader.discuss_idea(
            ideas=self.ideas, config=self.config
        )
        yield summarized_idea, self.leader

        # write one proposal
        related_papers = self.paper_db.match(
            query=summarized_idea.content
            if summarized_idea.content
            else self.leader.profile.bio,
            paper_profiles=available_papers,
            num=2,
        )
        proposal = self.leader.write_proposal(
            idea=summarized_idea,
            papers=related_papers,
            config=self.config,
        )
        yield proposal, self.leader
