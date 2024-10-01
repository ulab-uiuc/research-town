import itertools
import math
import random

from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple, Union

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from ..dbs import LogDB, PaperDB, ProgressDB
from .env_base import BaseEnv


class ProposalWritingEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        config: Config,
        agent_manager: AgentManager,
    ) -> None:
        super().__init__(
            name=name,
            config=config,
        )
        self.log_db = log_db
        self.progress_db = progress_db
        self.paper_db = paper_db
        self.agent_manager = agent_manager

    @beartype
    def on_enter(self, **context: Any) -> None:
        leader = context['leader']
        self.contexts = context['contexts']
        self.leader = leader
        self.members = self.agent_manager.sample_members()

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        self.env_run_num += 1
        if self.env_run_num > self.config.param.max_env_run_num:
            return 'error', {}
        else:
            return 'start_review', {'proposal': self.proposal, 'leader': self.leader}

    @beartype
    def run(
        self,
    ) -> Generator[
        Tuple[
            Union[
                List[Insight],
                List[Idea],
                List[Proposal],
                List[Review],
                List[Rebuttal],
                List[MetaReview],
            ],
            Agent,
        ],
        None,
        None,
    ]:
        # Each member reviews literature
        insights: List[Insight] = []
        keywords: List[str] = []
        ideas: List[Idea] = []
        for member in self.members:
            related_papers = self.paper_db.search_papers(
                query=';'.join(self.contexts),
                num=2,
            )
            summary, keywords, insight = member.review_literature(
                papers=related_papers,
                contexts=self.contexts,
                config=self.config,
            )
            yield [insight], member
            insights.append(insight)
            keywords.extend(keywords)

        keywords = sorted(keywords, key=lambda x: x[1], reverse=True)

        for member in self.members:
            related_papers = self.paper_db.search_papers(
                query=insight.content,
                author=member.profile.name,
                domain=keywords[0] + member.profile.domain[0]
                if member.profile.domain
                else keywords[0],
                num=7,
            )
            idea = member.brainstorm_idea(
                papers=related_papers, insights=insights, config=self.config
            )
            ideas.append(idea)
            yield [idea], member

        # Leader discusses ideas

        # Sampling Proposals
        idea_sample_num = self.config.param.idea_sample_num
        proposal_num = self.config.param.proposal_num

        total_ideas = len(ideas)

        # Error Handling
        if idea_sample_num > total_ideas:
            raise ValueError(
                f'idea_sample_num ({idea_sample_num}) cannot be greater than the number of available ideas ({total_ideas}).'
            )

        # Calculate the total number of possible unique combinations
        total_combinations = math.comb(total_ideas, idea_sample_num)

        if proposal_num > total_combinations:
            raise ValueError(
                f'proposal_num ({proposal_num}) cannot be greater than the total number of unique combinations ({total_combinations}).'
            )

        # Generate all possible unique combinations
        all_combinations = list(itertools.combinations(ideas, idea_sample_num))

        # Randomly sample the required number of unique combinations
        sampled_combinations = random.sample(all_combinations, proposal_num)

        proposals = []

        for _, idea_subset in enumerate(sampled_combinations, 1):
            # Leader discusses the subset of ideas to generate a summarized idea
            summarized_idea = self.leader.discuss_idea(
                ideas=idea_subset, contexts=self.contexts, config=self.config
            )
            yield summarized_idea, self.leader

            # Write Proposal
            query = summarized_idea.content or self.leader.profile.bio
            related_papers = self.paper_db.search_papers(
                query=query,
                domain=self.leader.profile.domain[0]
                if self.leader.profile.domain
                else None,
                num=2,
            )
            proposal = self.leader.write_proposal(
                idea=summarized_idea,
                papers=related_papers,
                config=self.config,
                proposal_num=self.config.param.proposal_num,
            )
            # Add the generated proposal to the proposals list
            proposals.append(proposal)
            yield proposal, self.leader

        # Assign the list of proposals to self.proposal
        self.proposal = proposals
