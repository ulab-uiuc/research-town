from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Idea, Insight, Progress, Proposal
from ..dbs import LogDB, PaperDB, ProgressDB
from ..utils.sampler import sample_ideas
from .env_base import BaseEnv


class ProposalWritingwithoutRAGEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        config: Config,
        agent_manager: AgentManager,
    ) -> None:
        super().__init__(name=name, config=config)
        self.log_db = log_db
        self.progress_db = progress_db
        self.paper_db = paper_db
        self.agent_manager = agent_manager
        self.proposals: List[Proposal] = []

    @beartype
    def on_enter(self, **context: Any) -> None:
        # Assign leader and members from context or sample them
        self.leader = context.get('leader')#, self.agent_manager.sample_leader())
        self.members = context.get('members')#, self.agent_manager.sample_members())

        if 'contexts' not in context:
            raise ValueError("'contexts' is required in the context.")
        self.contexts = context['contexts']
    

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        # Update environment run number and handle limits
        self.env_run_num += 1
        if self.env_run_num > self.config.param.max_env_run_num:
            return 'error', {}  # Return error if max run limit exceeded
        return 'start_review', {'proposals': self.proposals, 'leader': self.leader}

    @beartype
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        insights: List[Insight] = []
        ideas: List[Idea] = []

        researchers = self.members + [self.leader]

        # Step 1: Researchers review literature and gather insights
        for researcher in researchers:
            summary, keywords, insight = researcher.review_literature(
                contexts=self.contexts,
                config=self.config,
            )

            yield insight, researcher
            insights.append(insight)

        # Step 3: Researchers brainstorm ideas based on their insights
        for researcher in researchers:
            idea = researcher.brainstorm_idea(insights=insights, config=self.config)
            yield idea, researcher
            ideas.append(idea)

        # Step 4: Leader summarizes ideas and writes proposals
        idea_combos = sample_ideas(ideas, self.config.param.proposal_num)
        for idea_combo in idea_combos:
            summarized_idea = self.leader.summarize_idea(
                ideas=idea_combo, contexts=self.contexts, config=self.config
            )
            yield summarized_idea, self.leader

            proposal = self.leader.write_proposal(
                idea=summarized_idea,
                config=self.config,
            )
            yield proposal, self.leader
            self.proposals.append(proposal)
