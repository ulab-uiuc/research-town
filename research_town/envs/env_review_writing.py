from collections import Counter

from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Union, Tuple

from ..agents.agent_base import BaseResearchAgent
from ..configs import Config
from ..dbs import (
    PaperDB,
    ResearcherDB,
    Rebuttal,
    Researcher,
    Review,
)
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'participant', 'chair'] | None


class ReviewWritingEnv(BaseEnv):
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
        self.paper = kwargs['paper']

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
            raise ValueError('At least one leader is required to write rebuttal.')
        if 'reviewer' not in agent_roles:
            raise ValueError('At least one reviewer is required to write review.')
        if 'chair' not in agent_roles:
            raise ValueError('At least one chair is required to write meta-review.')
        if 'participant' in agent_roles:
            raise ValueError('participant role is not allowed in peer review.')

        counter = Counter(agent_roles)
        if counter['leader'] != 1:
            raise ValueError('Exactly one leader is required to write rebuttal.')
        if counter['chair'] != 1:
            raise ValueError('Exactly one chair is required to write meta-review.')

        self.chair = [agent for agent in self.agents if agent.role == 'chair'][0]
        self.leader = [
            agent for agent in self.agents if agent.role == 'leader'
        ][0]
        self.reviewers = [agent for agent in self.agents if agent.role == 'reviewer']

    @beartype
    def on_exit(self) -> bool:
        if self.stop_flag:
            raise NotImplementedError('Stop signal is not implemented yet.')
        for review in self.reviews:
            self.progress_db.add(review)
        self.env_run_num += 1
        return True

    @beartype
    def run(self) -> Tuple[Any, BaseResearchAgent]:
        # Paper Reviewing
        self.reviews: List[Review] = []
        for reviewer in self.reviewers:
            review = reviewer.write_review(
                paper=self.paper,
                config=self.config,
            )
            yield review, reviewer

        # Rebuttal Submitting
        self.rebuttals: List[Rebuttal] = []
        for review in self.reviews:
            rebuttal = self.leader.write_rebuttal(
                paper=self.paper,
                review=review,
                config=self.config,
            )
            yield rebuttal, self.leader

        # Paper Meta Reviewing
        self.meta_review = self.chair.write_meta_review(
            paper=self.paper,
            reviews=self.reviews,
            rebuttals=self.rebuttals,
            config=self.config,
        )
        yield self.meta_review, self.chair
