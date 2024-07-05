from beartype import beartype
from beartype.typing import Any, Dict, List, Literal, Optional, Tuple

from ..configs import Config
from ..dbs import (
    AgentProfile,
    PaperProfile,
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReviewForPaperSubmission,
    ResearchPaperSubmission,
    ResearchRebuttalForPaperSubmission,
    ResearchReviewForPaperSubmission,
)
from ..utils.agent_collector import bfs
from ..utils.agent_prompter import (
    find_collaborators_prompting,
    read_paper_prompting,
    review_paper_prompting,
    review_score_prompting,
    summarize_ideas_prompting,
    think_idea_prompting,
    write_meta_review_prompting,
    write_paper_prompting,
    write_rebuttal_prompting,
)
from ..utils.agent_role_verifier import (
    chair_required,
    proj_leader_required,
    proj_participant_required,
    reviewer_required,
)
from ..utils.serializer import Serializer

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair']


class BaseResearchAgent(object):
    def __init__(
        self,
        agent_profile: AgentProfile,
        model_name: str,
        agent_role: Optional[Role] = None,
    ) -> None:
        self.profile: AgentProfile = agent_profile
        self.memory: Dict[str, str] = {}
        self.role: Role | None = agent_role
        self.model_name: str = model_name
        self.serializer = Serializer()

    @beartype
    def get_profile(self, author_name: str) -> AgentProfile:
        # TODO: db get based on name
        # TODO: need rebuild
        agent_profile = AgentProfile(
            name='Geoffrey Hinton',
            bio='A researcher in the field of neural network.',
        )
        return agent_profile

    @beartype
    def find_collaborators(
        self,
        paper: PaperProfile,
        parameter: float = 0.5,
        max_number: int = 3,
    ) -> List[AgentProfile]:
        # TODO: need rebuild
        start_author: List[str] = (
            [self.profile.name] if self.profile.name is not None else []
        )
        graph, _, _ = bfs(author_list=start_author, node_limit=max_number)
        collaborators = list(
            {name for pair in graph for name in pair if name != self.profile.name}
        )
        self_profile: Dict[str, str] = (
            {self.profile.name: self.profile.bio}
            if self.profile.name is not None and self.profile.bio is not None
            else {}
        )
        collaborator_profiles: Dict[str, str] = {}
        for author in collaborators:
            author_bio = self.get_profile(author).bio
            if author_bio is not None:
                collaborator_profiles[author] = author_bio
        paper_serialize: Dict[str, str] = (
            {paper.title: paper.abstract}
            if paper.title is not None and paper.abstract is not None
            else {}
        )
        result = find_collaborators_prompting(
            input=paper_serialize,
            self_profile=self_profile,
            collaborator_profiles=collaborator_profiles,
            parameter=parameter,
            max_number=max_number,
        )
        collaborators_list = []
        for collaborator in collaborators:
            if collaborator in result:
                collaborators_list.append(self.get_profile(collaborator))
        return collaborators_list

    @beartype
    def get_co_author_relationships(
        self, agent_profile: AgentProfile, max_node: int
    ) -> Tuple[
        List[Tuple[str, str]],
        Dict[str, List[Dict[str, Any]]],
        Dict[str, List[Dict[str, Any]]],
    ]:
        # TODO: need rebuild
        start_author: List[str] = (
            [self.profile.name] if self.profile.name is not None else []
        )
        graph, node_feat, edge_feat = bfs(author_list=start_author, node_limit=max_node)
        return graph, node_feat, edge_feat

    # =======================================

    def assign_role(self, role: Role) -> None:
        self.role = role

    @beartype
    @proj_participant_required
    def review_literature(
        self, papers: List[PaperProfile], domains: List[str], config: Config
    ) -> List[ResearchInsight]:
        serialized_papers = self.serializer.serialize(papers)
        serialized_profile = self.serializer.serialize(self.profile)
        insight_contents = read_paper_prompting(
            profile=serialized_profile,
            papers=serialized_papers,
            domains=domains,
            model_name=self.model_name,
            prompt_template_query=config.prompt_template.query_paper,
            prompt_template_read=config.prompt_template.read_paper,
        )
        insights: List[ResearchInsight] = []
        for content in insight_contents:
            insights.append(ResearchInsight(content=content))
        return insights

    @beartype
    @proj_participant_required
    def brainstorm_idea(
        self, insights: List[ResearchInsight], config: Config
    ) -> ResearchIdea:
        serialized_insights = self.serializer.serialize(insights)
        idea_content = think_idea_prompting(
            insights=serialized_insights,
            model_name=self.model_name,
            prompt_template=config.prompt_template.think_idea,
        )[0]
        return ResearchIdea(content=idea_content)

    @beartype
    @proj_participant_required
    def discuss_idea(self, ideas: List[ResearchIdea], config: Config) -> ResearchIdea:
        serialized_ideas = self.serializer.serialize(ideas)
        idea_summarized = summarize_ideas_prompting(
            ideas=serialized_ideas,
            model_name=self.model_name,
            prompt_template=config.prompt_template.summarize_ideas,
        )[0]
        return ResearchIdea(content=idea_summarized)

    @beartype
    @proj_leader_required
    def write_paper(
        self, idea: ResearchIdea, papers: List[PaperProfile], config: Config
    ) -> ResearchPaperSubmission:
        serialized_idea = self.serializer.serialize(idea)
        serialized_papers = self.serializer.serialize(papers)
        paper_abstract = write_paper_prompting(
            idea=serialized_idea,
            papers=serialized_papers,
            model_name=self.model_name,
            prompt_template=config.prompt_template.write_paper,
        )[0]
        return ResearchPaperSubmission(abstract=paper_abstract)

    @beartype
    @reviewer_required
    def write_paper_review(
        self, paper: PaperProfile, config: Config
    ) -> ResearchReviewForPaperSubmission:
        serialized_paper = self.serializer.serialize(paper)
        paper_review = review_paper_prompting(
            paper=serialized_paper,
            model_name=self.model_name,
            prompt_template=config.prompt_template.review_paper,
        )[0]
        review_score = review_score_prompting(
            paper_review=paper_review,
            model_name=self.model_name,
            prompt_template=config.prompt_template.review_score,
        )
        return ResearchReviewForPaperSubmission(
            paper_pk=paper.pk,
            reviewer_pk=self.profile.pk,
            content=paper_review,
            score=review_score,
        )

    @beartype
    @chair_required
    def write_meta_review(
        self,
        paper: PaperProfile,
        reviews: List[ResearchReviewForPaperSubmission],
        rebuttals: List[ResearchRebuttalForPaperSubmission],
        config: Config,
    ) -> ResearchMetaReviewForPaperSubmission:
        serialized_paper = self.serializer.serialize(paper)
        serialized_reviews = self.serializer.serialize(reviews)
        serialized_rebuttals = self.serializer.serialize(rebuttals)

        meta_review = write_meta_review_prompting(
            paper=serialized_paper,
            reviews=serialized_reviews,
            rebuttals=serialized_rebuttals,
            model_name=self.model_name,
            prompt_template=config.prompt_template.write_meta_review,
        )
        review_decision = 'accept' in meta_review[0].lower()

        return ResearchMetaReviewForPaperSubmission(
            paper_pk=paper.pk,
            area_chair_pk=self.profile.pk,
            reviewer_pks=[review.reviewer_pk for review in reviews],
            author_pk=self.profile.pk,
            content=meta_review[0],
            decision=review_decision,
        )

    @beartype
    @proj_leader_required
    def write_rebuttal(
        self,
        paper: PaperProfile,
        review: ResearchReviewForPaperSubmission,
        config: Config,
    ) -> ResearchRebuttalForPaperSubmission:
        serialized_paper = self.serializer.serialize(paper)
        serialized_review = self.serializer.serialize(review)

        rebuttal_content = write_rebuttal_prompting(
            paper=serialized_paper,
            review=serialized_review,
            model_name=self.model_name,
            prompt_template=config.prompt_template.write_rebuttal,
        )[0]

        return ResearchRebuttalForPaperSubmission(
            paper_pk=paper.pk,
            reviewer_pk=review.reviewer_pk,
            author_pk=self.profile.pk,
            content=rebuttal_content,
        )
