from beartype import beartype
from beartype.typing import Any, Dict, Generator, Tuple

from ..agents import Agent, AgentManager
from ..configs import Config
from ..dbs import LogDB, PaperDB, Progress, ProgressDB
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
        self.members = self.agent_manager.find_members(leader.profile)

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        self.env_run_num += 1
        if self.env_run_num > self.config.param.max_env_run_num:
            return 'error', {}
        else:
            return 'start_review', {'proposal': self.proposal, 'leader': self.leader}

    @beartype
    def run(self) -> Generator[Tuple[Progress, Agent], None, None]:
        available_papers = list(self.paper_db.data.values())

        # Each member reviews literature
        all_insights = []
        for member in self.members:
            related_papers = self.paper_db.match(
                query=member.profile.bio,
                papers=available_papers,
                num=2,
            )
            insights = member.review_literature(
                papers=related_papers,
                domains=['machine learning'],
                contexts=self.contexts,
                config=self.config,
            )
            all_insights.extend(insights)
            for insight in insights:
                yield insight, member

        # Brainstorm ideas
        ideas = []
        for member in self.members:
            idea = member.brainstorm_idea(insights=all_insights, config=self.config)
            ideas.append(idea)
            yield idea, member

        # Leader discusses ideas
        summarized_idea = self.leader.discuss_idea(ideas=ideas, config=self.config)
        yield summarized_idea, self.leader

        # Write Proposal
        query = summarized_idea.content or self.leader.profile.bio
        related_papers = self.paper_db.match(
            query=query,
            papers=available_papers,
            num=2,
        )
        proposal = self.leader.write_proposal(
            idea=summarized_idea,
            papers=related_papers,
            config=self.config,
        )
        yield proposal, self.leader

        self.proposal = proposal  # Store the proposal for use in on_exit
