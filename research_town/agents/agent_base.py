from typing import Any, Dict, List, Tuple

from ..utils.agent_prompter import (
    communicate_with_multiple_researchers_prompting,
    find_collaborators_prompting,
    generate_ideas_prompting,
    make_review_decision_prompting,
    rebut_review_prompting,
    review_paper_prompting,
    review_score_prompting,
    summarize_research_direction_prompting,
    summarize_research_field_prompting,
    write_paper_abstract_prompting,
)
from ..utils.author_collector import bfs
from ..utils.paper_collector import get_paper_list

ATOM_NAMESPACE = "{http://www.w3.org/2005/Atom}"

class BaseResearchAgent(object):
    def __init__(self, name: str) -> None:
        self.profile = self.get_profile(name)
        self.name = name
        self.memory: Dict[str, str] = {}

    def get_profile(self, author_name: str) -> Dict[str, Any]:
        papers_list = get_paper_list(author_name)
        if papers_list:
            personal_info = "; ".join(
                [f"{details['Title & Abstract']}" for details in papers_list]
            )
            profile_info = summarize_research_direction_prompting(personal_info)
            return {"name": author_name, "profile": profile_info[0]}
        else:
            return {"info": "fail!"}

    def communicate(self, message: Dict[str, str]) -> str:
        return communicate_with_multiple_researchers_prompting(message)[0]

    def read_paper(
        self, papers: Dict[str, Dict[str, List[str]]], domain: str
    ) -> str:
        trend = summarize_research_field_prompting(
            profile=self.profile,
            keywords=[domain],
            papers=papers,
        )
        trend_output = trend[0]
        return trend_output

    def find_collaborators(self, input: Dict[str, str], parameter: float = 0.5, max_number: int = 3) -> List[str]:
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

    def get_co_author_relationships(self, name: str, max_node: int) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        start_author = [name]
        graph, node_feat, edge_feat = bfs(
            author_list=start_author, node_limit=max_node)
        return graph, node_feat, edge_feat

    def generate_idea(
        self, papers: Dict[str, Dict[str, List[str]]], domain: str
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

    def write_paper(self, input: List[str], papers: Dict[str, Dict[str, List[str]]]) -> str:
        paper_abstract = write_paper_abstract_prompting(input, papers)
        return paper_abstract[0]

    def review_paper(self, paper: Dict[str, str]) -> Tuple[int, str]:
        paper_review = review_paper_prompting(paper)[0]
        print(paper_review)
        review_score = review_score_prompting(paper_review)
        print(review_score, paper_review)
        return review_score, paper_review

    def make_review_decision(
        self, submission: Dict[str, str], review: Dict[str, Tuple[int, str]]
    ) -> Tuple[bool, str]:
        meta_review = make_review_decision_prompting(submission, review)
        if "accept" in meta_review[0].lower():
            review_decision = True
        else:
            review_decision = False
        return review_decision, meta_review[0]

    def rebut_review(self, submission: Dict[str, str], review: Dict[str, Tuple[int, str]], decision: Dict[str, Tuple[bool, str]]) -> str:
        rebut_review = rebut_review_prompting(submission, review, decision)
        return rebut_review[0]
