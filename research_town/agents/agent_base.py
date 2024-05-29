from datetime import datetime
from typing import Any, Dict, List, Tuple

from beartype import beartype

from ..dbs import (
    AgentAgentDiscussionLog,
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
    AgentProfile,
    PaperProfile,
    ResearchIdea,
    ResearchTrend,
    ResearchPaperSubmission
)
from ..utils.agent_collector import bfs
from ..utils.agent_prompter import (
    communicate_with_multiple_researchers_prompting,
    find_collaborators_prompting,
    generate_ideas_prompting,
    make_review_decision_prompting,
    rebut_review_prompting,
    review_paper_prompting,
    review_score_prompting,
    summarize_research_field_prompting,
    write_paper_abstract_prompting,
)


class BaseResearchAgent(object):
    def __init__(self,
        agent_profile: AgentProfile,
        model_name: str
    ) -> None:
        self.profile: AgentProfile = agent_profile
        self.memory: Dict[str, str] = {}
        self.model_name: str = model_name

    @beartype
    def get_profile(self, author_name: str) -> AgentProfile:
        # TODO: db get based on name
        # TODO: need rebuild
        agent_profile = AgentProfile(
            name='Geoffrey Hinton',
            bio="A researcher in the field of neural network.",
        )
        return agent_profile


    @beartype
    def find_collaborators(
        self,
        paper: PaperProfile,
        parameter: float = 0.5,
        max_number: int = 3
    ) -> List[AgentProfile]:
        # TODO: need rebuild
        start_author: List[str] = [
            self.profile.name] if self.profile.name is not None else []
        graph, _, _ = bfs(
            author_list=start_author, node_limit=max_number)
        collaborators = list(
            {name for pair in graph for name in pair if name != self.profile.name})
        self_profile: Dict[str, str] = {
            self.profile.name: self.profile.bio} if self.profile.name is not None and self.profile.bio is not None else {}
        collaborator_profiles: Dict[str, str] = {}
        for author in collaborators:
            author_bio = self.get_profile(author).bio
            if author_bio is not None:
                collaborator_profiles[author] = author_bio
        paper_serialize: Dict[str, str] = {
            paper.title: paper.abstract} if paper.title is not None and paper.abstract is not None else {}
        result = find_collaborators_prompting(
            paper_serialize,
            self_profile,
            collaborator_profiles,
            parameter,
            max_number
        )
        collaborators_list = []
        for collaborator in collaborators:
            if collaborator in result:
                collaborators_list.append(self.get_profile(collaborator))
        return collaborators_list

    @beartype
    def get_co_author_relationships(
        self,
        agent_profile: AgentProfile,
        max_node: int
    ) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        # TODO: need rebuild
        start_author: List[str] = [
            self.profile.name] if self.profile.name is not None else []
        graph, node_feat, edge_feat = bfs(
            author_list=start_author, node_limit=max_node)
        return graph, node_feat, edge_feat


    @beartype
    def read_paper(
        self,
        papers: List[PaperProfile],
        domains: List[str]
    ) -> List[ResearchTrend]:
        papers = self.serializer.serialize(papers)
        profiles = self.serializer.serialize([self.profile])
        trend_contents = summarize_research_trend_prompting(
            profiles=profiles,
            papers=papers,
            domains=domains,
            model_name=self.model_name
        )
        trends: List[ResearchTrend] = []
        for content in trend_contents:
            trends.append(ResearchTrend(content=content))
        return trends
    

    @beartype
    def think_idea(
        self,
        trends: List[ResearchTrend],
    ) -> List[ResearchIdea]:
        trends = self.serializer.serialize(trends)
        idea_contents: List[str] = []
        for trend in trends:
            idea_contents.append(generate_idea_prompting(
                trend=trend,
                model_name=self.model_name
            )[0])
        ideas: List[ResearchIdea] = []
        for content in idea_contents:
            ideas.append(ResearchIdea(content=content))
        return ideas


    @beartype
    def write_paper(
        self,
        ideas: List[str],
        papers: List[PaperProfile]
    ) -> ResearchPaperSubmission:
        papers = self.serializer.serialize(papers)
        paper_abstract = write_paper_prompting(
            ideas=ideas,
            papers=papers_dict,
            model_name=self.model_name
        )[0]
        return ResearchPaperSubmission(abstract=paper_abstract)

    @beartype
    def review_paper(
        self,
        paper: PaperProfile
    ) -> AgentPaperReviewLog:
        papers_dict = self.serializer.serialize([paper])
        paper_review = review_paper_prompting(
            paper=papers_dict,
            model_name=self.model_name
        )[0]
        review_score = review_score_prompting(
            paper_review=paper_review,
            model_name=self.model_name
        )
        return AgentPaperReviewLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            review_content=paper_review,
            review_score=review_score
        )

    @beartype
    def write_meta_review(
        self,
        paper: PaperProfile,
        review_logs: List[AgentPaperReviewLog]
    ) -> AgentPaperMetaReviewLog:
        papers_dict = self.serializer.serialize([paper])
        reviews_dict = self.serializer.serialize(review_logs)

        meta_review = make_review_decision_prompting(
            paper=papers_dict,
            review=reviews_dict,
            model_name=self.model_name
        )
        review_decision = "accept" in meta_review[0].lower()

        return AgentPaperMetaReviewLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            decision=review_decision,
            meta_review=meta_review[0],
        )

    @beartype
    def write_rebuttal(
        self,
        paper: PaperProfile,
        reviews: List[AgentPaperReviewLog],
    ) -> AgentPaperRebuttalLog:
        papers = self.serializer.serialize([paper])
        reviews = self.serializer.serialize(reviews)

        rebuttal_content = rebut_review_prompting(
            paper=papers,
            review=reviews,
            model_name=self.model_name
        )[0]

        return AgentPaperRebuttalLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            rebuttal_content=rebuttal_content
        )

    @beartype
    def discuss(
        self,
        message: AgentAgentDiscussionLog
    ) -> AgentAgentDiscussionLog:
        message = self.serializer.serialize([message])
        message_content = communicate_with_multiple_researchers_prompting(
            message=message,
            model_name=self.model_name
        )[0]
        return AgentAgentDiscussionLog(
            timestep=(int)(datetime.now().timestamp()),
            agent_from_pk=message.agent_from_pk,
            agent_to_pk=message.agent_to_pk,
            message=message_content
        )