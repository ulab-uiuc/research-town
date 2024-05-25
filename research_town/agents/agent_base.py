from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

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
    summarize_research_field_prompting,
    write_paper_abstract_prompting,
)


class BaseResearchAgent(object):
    def __init__(self, 
        agent_profile: AgentProfile,
    ) -> None:
        self.profile: AgentProfile = agent_profile
        self.memory: Dict[str, str] = {}

    def get_profile(self, author_name: str) -> AgentProfile:
        # TODO: db get based on name
        agent_profile = AgentProfile(
            name='Geoffrey Hinton',
            bio="A researcher in the field of neural network.",
        )
        return agent_profile

    def communicate(
        self,
        message: AgentAgentDiscussionLog
    ) -> AgentAgentDiscussionLog:
        # TODO: find a meaningful key
        message_dict = {message.agent_from_pk: message.message}
        message_content = communicate_with_multiple_researchers_prompting(
            message_dict
        )[0]
        discussion_log = AgentAgentDiscussionLog(
            timestep=(int)(datetime.now().timestamp()),
            agent_from_pk=message.agent_from_pk,
            agent_to_pk=message.agent_to_pk,
            message=message_content
        )
        return discussion_log

    def read_paper(
        self,
        papers: List[PaperProfile],
        domain: str
    ) -> str:
        papers_dict = {}
        for paper in papers:
            papers_dict[paper.pk] = {
                "abstract": [paper.abstract],
                "title": [paper.title]
            }
        trend = summarize_research_field_prompting(
            profile={
                "name": self.profile.name,
                "profile": self.profile.bio
            },
            keywords=[domain],
            papers=papers_dict
        )
        trend_output = trend[0]
        return trend_output

    def find_collaborators(
        self,
        paper: PaperProfile,
        parameter: float = 0.5,
        max_number: int = 3
    ) -> List[AgentProfile]:
        start_author = [self.profile.name]
        graph, _, _ = bfs(
            author_list=start_author, node_limit=max_number)
        collaborators = list(
            {name for pair in graph for name in pair if name != self.profile.name})
        self_profile = {self.profile.name: self.profile.bio}
        collaborator_profiles = {author: self.get_profile(
            author).bio for author in collaborators}
        paper_serialize = {paper.title: paper.abstract}
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

    def get_co_author_relationships(
        self,
        agent_profile: AgentProfile,
        max_node: int
    ) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        start_author = [self.name]
        graph, node_feat, edge_feat = bfs(
            author_list=start_author, node_limit=max_node)
        return graph, node_feat, edge_feat

    def generate_idea(
        self,
        papers: List[PaperProfile],
        domain: str
    ) -> List[str]:
        papers_dict = {}
        for paper_profile in papers:
            papers_dict[paper_profile.pk] = {
                "abstract": [paper_profile.abstract],
                "title": [paper_profile.title]
            }
        trends = summarize_research_field_prompting(
            profile={
                "name": self.profile.name,
                "profile": self.profile.bio
            },
            keywords=[domain],
            papers=papers_dict
        )
        ideas: List[str] = []
        for trend in trends:
            idea = generate_ideas_prompting(trend)[0]
            ideas.append(idea)

        return ideas

    def write_paper(
        self,
        research_ideas: List[str],
        papers: List[PaperProfile]
    ) -> PaperProfile:
        papers_dict = {}
        for paper_profile in papers:
            papers_dict[paper_profile.pk] = {
                "abstract": [paper_profile.abstract],
                "title": [paper_profile.title]
            }
        paper_abstract = write_paper_abstract_prompting(
            research_ideas, papers_dict)[0]
        paper_profile = PaperProfile(abstract=paper_abstract)
        return paper_profile

    def review_paper(
        self,
        paper: PaperProfile
    ) -> AgentPaperReviewLog:
        paper_dict = {paper.title: paper.abstract}
        paper_review = review_paper_prompting(paper_dict)[0]
        review_score = review_score_prompting(paper_review)

        return AgentPaperReviewLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            review_content=paper_review,
            review_score=review_score
        )

    def make_review_decision(
        self,
        paper: PaperProfile,
        review: List[AgentPaperReviewLog]
    ) -> AgentPaperMetaReviewLog:
        paper_dict = {paper.title: paper.abstract}
        review_dict = {}
        for agent_review_log in review:
            review_dict[agent_review_log.pk] = (
                agent_review_log.review_score, agent_review_log.review_content)

        meta_review = make_review_decision_prompting(paper_dict, review_dict)
        review_decision = "accept" in meta_review[0].lower()

        return AgentPaperMetaReviewLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            decision=review_decision,
            meta_review=meta_review[0],
        )

    def rebut_review(
        self,
        paper: PaperProfile,
        review: List[AgentPaperReviewLog],
        decision: List[AgentPaperMetaReviewLog]
    ) -> AgentPaperRebuttalLog:
        paper_dict = {paper.title: paper.abstract}
        review_dict = {}
        for agent_review_log in review:
            review_dict[agent_review_log.pk] = (
                agent_review_log.review_score, agent_review_log.review_content)

        decision_dict = {}
        for agent_meta_review_log in decision:
            decision_dict[agent_meta_review_log.pk] = (
                agent_meta_review_log.decision == "accept", agent_meta_review_log.meta_review)

        rebut_review = rebut_review_prompting(
            paper_dict, review_dict, decision_dict)[0]

        return AgentPaperRebuttalLog(
            timestep=(int)(datetime.now().timestamp()),
            paper_pk=paper.pk,
            agent_pk=self.profile.pk,
            rebuttal_content=rebut_review
        )
