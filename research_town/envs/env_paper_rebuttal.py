from beartype import beartype
from beartype.typing import Dict, Generator, List, Tuple, Union
import json
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
    ResearchPaperSubmission,
)
from .env_base import BaseMultiAgentEnv

LogType = Union[List[Dict[str, str]], None]
from ..utils.serializer import Serializer

class PaperRebuttalMultiAgentEnv(BaseMultiAgentEnv):
    def __init__(
        self,
        agent_profiles: List[AgentProfile],
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        env_db: EnvLogDB,
        config: Config,
    ) -> None:
        super().__init__(agent_profiles)
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
        self.log_reviews=dict()
        self.author_sub=dict()
        self.serializer = Serializer()

    @beartype
    def assign_roles(self, num: int = 1) -> None:
        for name in self.submission.keys():
            self.log_reviews[name]={'abstract':self.submission[name].abstract,'authors':self.submission[name].authors,
                                    'idea':self.submission[name].insight}
            self.author_sub[name]=self.submission[name]
        for name in self.log_reviews.keys():
            self.reviewer_mask_tem = self.reviewer_mask.copy()
            reviewer_profiles = []
            for agent_profile in self.agent_profiles:
                if agent_profile.pk not in self.log_reviews[name]:
                    reviewer_profiles.append(agent_profile)

            reviewer_pks = self.agent_db.match(
                idea=self.log_reviews[name]['abstract'], agent_profiles=reviewer_profiles, num=num
            )
            for index, agent_profile in enumerate(self.agent_profiles):
                if agent_profile.pk in reviewer_pks:
                    self.reviewer_mask[index] = True
            self.log_reviews[name]['reviewer_mask']=self.reviewer_mask

    @beartype
    def initialize_submission(self, paper_profile: Dict[str,ResearchPaperSubmission]) -> None:
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

    def next_step_(
        self):
        # yield from self.log('Paper Reviewing started')
        # Paper Reviewing
        for name in self.log_reviews.keys():
            self.reviews: List[AgentPaperReviewLog] = []
            self.rebuttals: List[AgentPaperRebuttalLog] = []
            self.meta_reviews: List[AgentPaperMetaReviewLog] = []
            for index, agent in enumerate(self.agents):
                if self.log_reviews[name]['reviewer_mask'][index]:
                    review = agent.write_paper_review(
                        paper=self.author_sub[name],
                        config=self.config,
                    )
                    self.reviews.append(review)
                    # yield from self.log(
                    #     f'Agent {agent.profile.name} gave review {str(review)}'
                    # )

            # yield from self.log('Paper Meta Reviewing started')
            # Paper Meta Reviewing
            for index, agent in enumerate(self.agents):
                if self.log_reviews[name]['reviewer_mask'][index]:
                    meta_review = agent.write_paper_meta_review(
                        paper=self.author_sub[name],
                        reviews=self.reviews,
                        config=self.config,
                    )
                    self.meta_reviews.append(meta_review)
                    # yield from self.log(
                    #     f'Agent {agent.profile.name} gave meta-review {str(meta_review)}'
                    # )

            # yield from self.log('Rebuttal Submitting started')
            # Rebuttal Submitting
            for index, agent in enumerate(self.agents):
                for review in self.reviews:
                    if self.reviewer_mask[index]:
                        rebuttal = agent.write_rebuttal(
                            paper=self.author_sub[name],
                            review=review,
                            config=self.config,
                        )
                        self.rebuttals.append(rebuttal)
                        # yield from self.log(
                        #     f'Agent {agent.profile.name} gave rebuttal {str(rebuttal)}'
                        # )

            # yield from self.log('PaperRebuttalMultiAgentEnv completed')
            last_reviews=[self.serializer.serialize(item) for item in self.reviews]
            last_rebuttals=[self.serializer.serialize(item) for item in self.rebuttals]
            last_meta_reviews=[self.serializer.serialize(item) for item in self.meta_reviews]

            self.log_reviews[name]['reviews']=last_reviews
            self.log_reviews[name]['rebuttals'] = last_rebuttals
            self.log_reviews[name]['meta_reviews'] = last_meta_reviews
        with open('all_saved_data.json', 'w') as json_file:
            json.dump(self.log_reviews, json_file)
        self.terminated = True