from typing import Any, Dict, List, Tuple

from ..utils.agent_prompter import (
    communicate_with_multiple_researchers_prompting,
    find_collaborators_prompting,
    generate_ideas_prompting,
    make_review_decision_prompting,
    rebut_review_prompting,
    review_paper_prompting,
    review_score_prompting,
    generate_profile,
    summarize_research_field_prompting,
    write_paper_abstract_prompting,
)
from ..utils.agent_collector import bfs
from ..utils.paper_collector import get_paper_list
from ..kbs.profile import AgentProfile, PaperProfile
from ..kbs.envlog import AgentPaperReviewLog, AgentPaperMetaReviewLog, AgentPaperRebuttalLog, AgentAgentDiscussionLog

class BaseResearchAgent(object):
    def __init__(self, name: str) -> None:
        self.profile = self.get_profile(name)
        self.memory: Dict[str, str] = {}

    def get_profile(self, author_name: str) -> AgentProfile:
        papers = get_paper_list(author_name)
        if papers:
            personal_info = "; ".join(
                [f"{details['Title & Abstract']}" for details in papers]
            )
            profile_info = generate_profile(personal_info)
            return {"name": author_name, "profile": profile_info[0]}
        else:
            return {"info": "fail!"}

    def communicate(
        self, 
        message: AgentAgentDiscussionLog
    ) -> AgentAgentDiscussionLog:
        return communicate_with_multiple_researchers_prompting(message)[0]

    def read_paper(
        self, 
        papers: Dict[str, PaperProfile], 
        domain: str
    ) -> str:
        trend = summarize_research_field_prompting(
            profile=self.profile,
            keywords=[domain],
            papers=papers,
        )
        trend_output = trend[0]
        return trend_output

    def find_collaborators(
        self, 
        paper: PaperProfile, 
        parameter: float = 0.5, 
        max_number: int = 3
    ) -> Dict[str, AgentProfile]:
        start_author = [self.name]
        graph, _, _ = bfs(
            author_list=start_author, node_limit=max_number)
        collaborators = list(
            {name for pair in graph for name in pair if name != self.name})
        self_profile = {self.name: self.profile["profile"]}
        collaborator_profiles = {author: self.get_profile(
            author)["profile"] for author in collaborators}
        result = find_collaborators_prompting(
            input, self_profile, collaborator_profiles, parameter, max_number)
        collaborators_list = [
            collaborator for collaborator in collaborators if collaborator in result]
        return collaborators_list

    def get_co_author_relationships(
        self, 
        agent_profile: AgentProfile,
        max_node: int
    ) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        start_author = [name]
        graph, node_feat, edge_feat = bfs(
            author_list=start_author, node_limit=max_node)
        return graph, node_feat, edge_feat

    def generate_idea(
        self, 
        papers: Dict[str, PaperProfile], 
        domain: str
    ) -> List[str]:

        trends = summarize_research_field_prompting(
            profile=self.profile,
            keywords=[domain],
            papers=papers,
        )
        ideas: List[str] = []
        for trend in trends:
            idea = generate_ideas_prompting(trend)[0]
            ideas.append(idea)

        return ideas

    def write_paper(
        self, 
        research_ideas: List[str], 
        papers: Dict[str, PaperProfile]
    ) -> PaperProfile:
        paper_abstract = write_paper_abstract_prompting(input, papers)
        return paper_abstract[0]

    def review_paper(
        self, 
        paper: PaperProfile
    ) -> AgentPaperReviewLog:
        paper_review = review_paper_prompting(paper)[0]
        review_score = review_score_prompting(paper_review)
        return review_score, paper_review

    def make_review_decision(
        self,
        paper: PaperProfile, 
        review: Dict[str, AgentPaperReviewLog]
    ) -> AgentPaperMetaReviewLog:
        meta_review = make_review_decision_prompting(paper, review)
        if "accept" in meta_review[0].lower():
            review_decision = True
        else:
            review_decision = False
        return review_decision, meta_review[0]

    def rebut_review(
        self, 
        paper: PaperProfile, 
        review: Dict[str, AgentPaperReviewLog], 
        decision: Dict[str, AgentPaperMetaReviewLog]
    ) -> AgentPaperRebuttalLog:
        rebut_review = rebut_review_prompting(paper, review, decision)
        return rebut_review[0]
