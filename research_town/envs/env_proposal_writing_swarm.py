from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple
from swarm import Swarm

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Insight, Progress, Proposal
from ..dbs import LogDB, PaperDB, ProgressDB
from .env_base import BaseEnv


class ProposalWritingSWARM(BaseEnv):
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
        self.client = Swarm()

    @beartype
    def on_enter(self, **context: Any) -> None:
        # Assign leader and members from context or sample them
        self.leader = context.get('leader', self.agent_manager.sample_leader())
        self.members = context.get('members', self.agent_manager.sample_members())

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
        accumulated_insights = []
        k = self.config.param.discussion_rounds

        for round_num in range(k):
            round_insights = []
            researchers = self.members + [self.leader]

            for researcher in researchers:
                search_query = (
                    ' '.join(insight.content for insight in accumulated_insights)
                    if accumulated_insights
                    else ';'.join(self.contexts)
                )
                related_papers = self.paper_db.search_papers(
                    query=search_query,
                    num=self.config.param.related_paper_num,
                )

                summary, keywords, insight = researcher.review_literature(
                    papers=related_papers,
                    contexts=self.contexts,
                    config=self.config,
                )

                # Generate insight based on RAG-enhanced context and prior discussions
                discussion_message = {
                    'role': 'user',
                    'content': f"Round {round_num + 1} discussion based on literature review summary: {summary} "
                    f"and keywords: {', '.join(keywords)}. Please provide your insights.",
                }

                response = self.client.run(
                    agent=researcher, messages=[discussion_message]
                )
                discussion_content = response.messages[-1]['content']

                # Log each researcher's insight
                discussion_insight = Insight(content=discussion_content)

                yield discussion_insight, researcher
                round_insights.append(discussion_insight)

            accumulated_insights.extend(round_insights)

        # Final step: Leader generates the proposal based on all accumulated insights
        combined_summary = ' '.join(insight.content for insight in accumulated_insights)
        final_related_papers = self.paper_db.search_papers(
            query=combined_summary,
            num=self.config.param.related_paper_num,
        )
        proposal = self.leader.write_proposal(
            idea=combined_summary,
            papers=final_related_papers,
            config=self.config,
        )

        yield proposal, self.leader
        self.proposals.append(proposal)
