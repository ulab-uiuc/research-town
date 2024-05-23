import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

from ..kbs.envlog import (
    AgentAgentDiscussionLog,
    AgentPaperMetaReviewLog,
    AgentPaperRebuttalLog,
    AgentPaperReviewLog,
)
from ..kbs.profile import AgentProfile, PaperProfile
from ..utils.agent_collector import bfs
from ..utils.agent_prompter import (
    communicate_with_multiple_researchers_prompting,
    find_collaborators_prompting,
    generate_ideas_prompting,
    generate_profile,
    make_review_decision_prompting,
    rebut_review_prompting,
    review_paper_prompting,
    review_score_prompting,
    summarize_research_field_prompting,
    write_paper_abstract_prompting,
)
from ..utils.paper_collector import get_paper_list


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
        papers: List[PaperProfile],
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
    ) -> List[AgentProfile]:
        start_author = [self.name]
        graph, _, _ = bfs(
            author_list=start_author, node_limit=max_number)
        collaborators = list(
            {name for pair in graph for name in pair if name != self.name})
        self_profile = {self.name: self.profile["profile"]}
        collaborator_profiles = {author: self.get_profile(
            author)["profile"] for author in collaborators}
        paper_serialize = {paper.title: paper.abstract}
        result = find_collaborators_prompting(
            paper_serialize, self_profile, collaborator_profiles, parameter, max_number)
        collaborators_list = [
            collaborator for collaborator in collaborators if collaborator in result]
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
        papers: List[PaperProfile]
    ) -> PaperProfile:
        paper_abstract = write_paper_abstract_prompting(input, papers)
        return paper_abstract[0]

    def review_paper(
        self,
        paper: PaperProfile
    ) -> AgentPaperReviewLog:
        paper_dict = {paper.title: paper.abstract}
        paper_review = review_paper_prompting(paper_dict)[0]
        review_score = review_score_prompting(paper_review)

        review_log = AgentPaperReviewLog()
        review_log.timestep = (int)(datetime.now().timestamp())
        review_log.review_id = str(uuid.uuid4())
        review_log.paper_id = paper.paper_id
        review_log.agent_id = self.profile.agent_id
        review_log.review_content = paper_review
        review_log.review_score = review_score

        return review_log

    def make_review_decision(
        self,
        paper: PaperProfile,
        review: List[AgentPaperReviewLog]
    ) -> AgentPaperMetaReviewLog:
        paper_dict = {paper.title: paper.abstract}
        review_dict = {}
        for agent_review_log in review:
            review_dict[agent_review_log.review_id] = (
                agent_review_log.review_score, agent_review_log.review_content)

        meta_review = make_review_decision_prompting(paper_dict, review_dict)
        review_decision = "accept" in meta_review[0].lower()

        meta_review_log = AgentPaperMetaReviewLog()
        meta_review_log.timestep = (int)(datetime.now().timestamp())
        meta_review_log.decision_id = str(uuid.uuid4())
        meta_review_log.paper_id = paper.paper_id
        meta_review_log.decision = "accept" if review_decision else "reject"
        meta_review_log.meta_review = meta_review[0]
        meta_review_log.agent_id = self.profile.agent_id
        return meta_review_log

    def rebut_review(
        self,
        paper: PaperProfile,
        review: List[AgentPaperReviewLog],
        decision: List[AgentPaperMetaReviewLog]
    ) -> AgentPaperRebuttalLog:
        paper_dict = {paper.title: paper.abstract}
        review_dict = {}
        for agent_review_log in review:
            review_dict[agent_review_log.review_id] = (
                agent_review_log.review_score, agent_review_log.review_content)

        decision_dict = {}
        for agent_meta_review_log in decision:
            decision_dict[agent_meta_review_log.decision_id] = (
                agent_meta_review_log.decision == "accept", agent_meta_review_log.meta_review)

        rebut_review = rebut_review_prompting(
            paper_dict, review_dict, decision_dict)

        rebuttal_log = AgentPaperRebuttalLog()
        rebuttal_log.timestep = (int)(datetime.now().timestamp())
        rebuttal_log.rebuttal_id = str(uuid.uuid4())
        rebuttal_log.paper_id = paper.paper_id
        rebuttal_log.agent_id = self.profile.agent_id
        rebuttal_log.rebuttal_content = rebut_review[0]
        return rebuttal_log
