from beartype import beartype
from beartype.typing import Any, Dict, Generator, List, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data import Idea, Insight, Progress
from ..dbs import LogDB, PaperDB, ProgressDB
from ..utils.sampler import sample_ideas
from .env_base import BaseEnv


class ProposalWritingwithRAGEnv(BaseEnv):
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
        # self.user_rag = use_rag

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
            return 'start_review', {'proposals': self.proposals, 'leader': self.leader}

    @beartype
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        # Each member reviews literature
        insights: List[Insight] = []
        keywords: List[str] = []
        ideas: List[Idea] = []
        for member in self.members:
            related_papers = self.paper_db.search_papers(
                query=';'.join(self.contexts),
                num=self.config.param.related_paper_num,
            )
            summary, keywords, insight = member.review_literature(
                papers=related_papers,
                contexts=self.contexts,
                config=self.config,
            )

            yield insight, member
            insights.append(insight)
            keywords.extend(keywords)

        keyword = sorted(keywords, key=lambda x: x[1], reverse=True)[0]

        for member in self.members:
            related_papers = self.paper_db.search_papers(
                query=insight.content,
                author=member.profile.name,
                domain=keyword + member.profile.domain[0]
                if member.profile.domain
                else keyword,
                num=self.config.param.related_paper_num,
            )
            idea = member.brainstorm_idea(
                papers=related_papers, insights=insights, config=self.config
            )
            yield idea, member
            ideas.append(idea)

        self.proposals = []
        idea_combos = sample_ideas(ideas, self.config.param.proposal_num)
        for idea_combo in idea_combos:
            summarized_idea = self.leader.summarize_idea(
                ideas=idea_combo, contexts=self.contexts, config=self.config
            )
            yield summarized_idea, self.leader

            related_papers = self.paper_db.search_papers(
                query=summarized_idea.content,
                num=self.config.param.related_paper_num,
            )
            proposal = self.leader.write_proposal(
                idea=summarized_idea,
                papers=related_papers,
                config=self.config,
            )
            yield proposal, self.leader
            self.proposals.append(proposal)
