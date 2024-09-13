from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Tuple, Union

from ..agents.agent_base import ResearchAgent
from ..configs import Config
from ..dbs import Idea, LogDB, PaperDB, Profile, ProfileDB, ProgressDB
from .env_base import BaseEnv

LogType = Union[List[Dict[str, str]], None]
Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


class ProposalWritingEnv(BaseEnv):
    def __init__(
        self,
        name: str,
        log_db: LogDB,
        progress_db: ProgressDB,
        paper_db: PaperDB,
        profile_db: ProfileDB,
        config: Config,
    ) -> None:
        super().__init__(
            name=name,
            log_db=log_db,
            progress_db=progress_db,
            paper_db=paper_db,
            profile_db=profile_db,
            config=config,
        )

    @beartype
    def on_enter(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        leader_profile = kwargs['leader_profile']
        self.leader = ResearchAgent(
            agent_profile=leader_profile,
            agent_role='leader',
            model_name=self.config.param.base_llm,
        )
        member_profiles = self.profile_db.match_member_profiles(
            leader=leader_profile,
            member_num=self.config.param.member_num,
        )
        self.members = [
            ResearchAgent(
                agent_profile=member_profile,
                agent_role='member',
                model_name=self.config.param.base_llm,
            )
            for member_profile in member_profiles
        ]

    @beartype
    def on_exit(self) -> Tuple[str, Dict[str, Any]]:
        self.env_run_num += 1
        return 'start_review', self.exit_data

    @beartype
    def run(self) -> Tuple[Any, Profile]:
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
                config=self.config,
            )
            all_insights.extend(insights)
            for insight in insights:
                yield insight, member.profile

        # Brainstorm ideas
        ideas: List[Idea] = []
        for member in self.members:
            idea = member.brainstorm_idea(insights=all_insights, config=self.config)
            ideas.append(idea)
            yield idea, member.profile

        # Leader discusses ideas
        summarized_idea = self.leader.discuss_idea(ideas=ideas, config=self.config)
        yield summarized_idea, self.leader.profile

        # Write Proposal
        query = (
            summarized_idea.content
            if summarized_idea.content
            else self.leader.profile.bio
        )
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
        yield proposal, self.leader.profile

        self.exit_data = {'proposal': proposal, 'leader_profile': self.leader.profile}