from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Idea, Insight, Progress
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
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        # Each member reviews literature
        insights: List[Insight] = []
        keywords: List[str] = []
        ideas: List[Idea] = []
        for member in self.members:
            summary, keywords, insight = member.review_literature(
                contexts=self.contexts,
                config=self.config,
            )
            yield insight, member
            insights.append(insight)
            keywords.extend(keywords)

        keywords = sorted(keywords, key=lambda x: x[1], reverse=True)

        for member in self.members:
            idea = member.brainstorm_idea(
                insights=insights, config=self.config
            )
            ideas.append(idea)
            yield idea, member

        # Leader discusses ideas
        summarized_idea = self.leader.discuss_idea(
            ideas=ideas, contexts=self.contexts, config=self.config
        )
        yield summarized_idea, self.leader

        # Write Proposal
        query = summarized_idea.content or self.leader.profile.bio
        proposal = self.leader.write_proposal(
            idea=summarized_idea,
            config=self.config,
        )
        yield proposal, self.leader

        self.proposal = proposal  # Store the proposal for use in on_exit
