from beartype import beartype
from beartype.typing import Dict, Generator, List, Literal, Tuple, Union

from ..configs import Config
from ..dbs import (
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfile,
    PaperProfileDB,
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'chair', 'proj_collaborator', 'proj_leader']


class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_roles: List[Role],
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        config: Config,
    ) -> None:
        super().__init__(agent_profiles=agent_profiles, agent_roles=agent_roles)
        self.decision = 'reject'
        self.submission = PaperProfile()
        self.reviewer_mask = [False] * len(agent_profiles)
        self.reviews: List[AgentPaperReviewLog] = []
        self.rebuttals: List[AgentPaperRebuttalLog] = []
        self.meta_reviews: List[AgentPaperMetaReviewLog] = []
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.env_db = env_db
        self.config = config

    @beartype
    def initialize_submission(self, paper_profile: PaperProfile) -> None:
        self.submission = paper_profile

    @beartype
    def submit_decision(self, decision_dict: Dict[str, Tuple[bool, str]]) -> None:
        decision_count = {'accept': 0, 'reject': 0}
        for _, decision in decision_dict.items():
            if decision[0]:
                decision_count['accept'] += 1
            else:
                decision_count['reject'] += 1
        count_max = 0
        for d, count in decision_count.items():
            if count > count_max:
                count_max = count
                self.decision = d

    def _step(
        self,
    ) -> Generator[LogType, None, None]:
        yield from self.log('Paper Reviewing started')
        # Paper Reviewing
        for agent in self.agents:
            if agent.role == 'reviewer':
                review = agent.write_paper_review(
                    paper=self.submission,
                    config=self.config,
                )
                self.reviews.append(review)
                yield from self.log(
                    f'Agent {agent.profile.name} gave review {str(review)}'
                )

        yield from self.log('Paper Meta Reviewing started')
        # Paper Meta Reviewing
        for agent in self.agents:
            if agent.role == 'chair':
                meta_review = agent.write_paper_meta_review(
                    paper=self.submission,
                    reviews=self.reviews,
                    config=self.config,
                )
                self.meta_reviews.append(meta_review)
                yield from self.log(
                    f'Agent {agent.profile.name} gave meta-review {str(meta_review)}'
                )

        yield from self.log('Rebuttal Submitting started')
        # Rebuttal Submitting
        for agent in self.agents:
            for review in self.reviews:
                if agent.role == 'proj_leader':
                    rebuttal = agent.write_rebuttal(
                        paper=self.submission,
                        review=review,
                        config=self.config,
                    )
                    self.rebuttals.append(rebuttal)
                    yield from self.log(
                        f'Agent {agent.profile.name} gave rebuttal {str(rebuttal)}'
                    )

        yield from self.log('PaperRebuttalMultiAgentEnv completed')
