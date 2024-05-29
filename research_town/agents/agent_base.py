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
    research_trend_prompting,
    prepare_research_trend_prompt_input,
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
        agent_profile = AgentProfile(
            name='Geoffrey Hinton',
            bio="A researcher in the field of neural network.",
        )
        return agent_profile

    @beartype
    def communicate(
        self,
        message: AgentAgentDiscussionLog
    ) -> AgentAgentDiscussionLog:
        # TODO: find a meaningful key
        message_dict: Dict[str, str] = {}
        if message.message is not None:
            message_dict[message.agent_from_pk] = message.message
        message_content = communicate_with_multiple_researchers_prompting(
            messages=message_dict,
            model_name=self.model_name
        )[0]
        discussion_log = AgentAgentDiscussionLog(
            timestep=(int)(datetime.now().timestamp()),
            agent_from_pk=message.agent_from_pk,
            agent_to_pk=message.agent_to_pk,
            message=message_content
        )
        return discussion_log

    @beartype
    def read_paper(
        self,
        papers: List[PaperProfile],
        domain: str
    ) -> str:
        prompt_input = prepare_research_trend_prompt_input(papers, self.profile, domain)
        trend_output = research_trend_prompting(
            profile=prompt_input["profile"],
            keywords=prompt_input["keywords"],
            papers=prompt_input["papers"],
            model_name=self.model_name
        )
        return trend_output

    @beartype
    def find_collaborators(
        self,
        paper: PaperProfile,
        parameter: float = 0.5,
        max_number: int = 3
    ) -> List[AgentProfile]:
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
        start_author: List[str] = [
            self.profile.name] if self.profile.name is not None else []
        graph, node_feat, edge_feat = bfs(
            author_list=start_author, node_limit=max_node)
        return graph, node_feat, edge_feat

    def generate_idea(
        self,
        papers: List[PaperProfile],
        domain: str
    ) -> List[str]:
        papers_dict: Dict[str, Dict[str, List[str]]] = {}
        for paper_profile in papers:
            papers_dict[paper_profile.pk] = {}
            if paper_profile.abstract is not None:
                papers_dict[paper_profile.pk]["abstract"] = [
                    paper_profile.abstract]
            if paper_profile.title is not None:
                papers_dict[paper_profile.pk]["title"] = [paper_profile.title]
        profile: Dict[str, str] = {}
        if self.profile.name is not None:
            profile["name"] = self.profile.name
        if self.profile.bio is not None:
            profile["profile"] = self.profile.bio
        trends = summarize_research_field_prompting(
            profile=profile,
            keywords=[domain],
            papers=papers_dict,
            model_name=self.model_name
        )
        ideas: List[str] = []
        for trend in trends:
            idea = generate_ideas_prompting(
                trend=trend,
                model_name=self.model_name
            )[0]
            ideas.append(idea)

        return ideas

    @beartype
    def write_paper(
        self,
        research_ideas: List[str],
        papers: List[PaperProfile]
    ) -> PaperProfile:
        papers_dict: Dict[str, Dict[str, List[str]]] = {}
        for paper_profile in papers:
            papers_dict[paper_profile.pk] = {}
            if paper_profile.abstract is not None:
                papers_dict[paper_profile.pk]["abstract"] = [
                    paper_profile.abstract]
            if paper_profile.title is not None:
                papers_dict[paper_profile.pk]["title"] = [paper_profile.title]
        paper_abstract = write_paper_abstract_prompting(
            ideas=research_ideas,
            papers=papers_dict,
            model_name=self.model_name
        )[0]
        paper_profile = PaperProfile(abstract=paper_abstract)
        return paper_profile

    @beartype
    def review_paper(
        self,
        paper: PaperProfile
    ) -> AgentPaperReviewLog:
        paper_dict:  Dict[str, str] = {
            paper.title: paper.abstract} if paper.title is not None and paper.abstract is not None else {}
        paper_review = review_paper_prompting(
            paper=paper_dict,
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
    def make_review_decision(
        self,
        paper: PaperProfile,
        review: List[AgentPaperReviewLog]
    ) -> AgentPaperMetaReviewLog:
        paper_dict: Dict[str, str] = {
            paper.title: paper.abstract} if paper.title is not None and paper.abstract is not None else {}
        review_dict: Dict[str, Tuple[int, str]] = {}
        for agent_review_log in review:
            if agent_review_log.review_score is not None and agent_review_log.review_content is not None:
                review_dict[agent_review_log.pk] = (
                    agent_review_log.review_score, agent_review_log.review_content)

        meta_review = make_review_decision_prompting(
            paper=paper_dict,
            review=review_dict,
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
    def rebut_review(
        self,
        paper: PaperProfile,
        review: List[AgentPaperReviewLog],
        decision: List[AgentPaperMetaReviewLog]
    ) -> AgentPaperRebuttalLog:
        paper_dict: Dict[str, str] = {
            paper.title: paper.abstract} if paper.title is not None and paper.abstract is not None else {}
        review_dict: Dict[str, Tuple[int, str]] = {}
        for agent_review_log in review:
            if agent_review_log.review_score is not None and agent_review_log.review_content is not None:
                review_dict[agent_review_log.pk] = (
                    agent_review_log.review_score, agent_review_log.review_content)

        decision_dict: Dict[str, Tuple[bool, str]] = {}
        for agent_meta_review_log in decision:
            if agent_meta_review_log.decision is not None and agent_meta_review_log.meta_review is not None:
                decision_dict[agent_meta_review_log.pk] = (
                    agent_meta_review_log.decision, agent_meta_review_log.meta_review)

        rebut_review = rebut_review_prompting(
            paper=paper_dict,
            review=review_dict,
            decision=decision_dict,
            model_name=self.model_name
        )[0]

        return AgentPaperRebuttalLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            rebuttal_content=rebut_review
        )
