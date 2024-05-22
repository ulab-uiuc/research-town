import datetime
from typing import Any, Dict, List, Tuple
from xml.etree import ElementTree

import requests

from ..utils.agent_prompting import (
    communicate_with_multiple_researchers_prompting,
    find_collaborators_prompting,
    generate_ideas_prompting,
    review_paper_prompting,
    summarize_research_direction_prompting,
    summarize_research_field_prompting,
    write_paper_abstract_prompting,
)
from ..utils.author_relation import bfs
from ..utils.paper_collection import get_bert_embedding

ATOM_NAMESPACE = "{http://www.w3.org/2005/Atom}"

class BaseResearchAgent(object):
    def __init__(self, name: str) -> None:
        self.profile = self.get_profile(name)
        self.name = name
        self.memory: Dict[str, str] = {}

    def find_text(self, element: ElementTree.Element, path: str) -> str:
        found_element = element.find(path)
        if found_element is not None and found_element.text is not None:
            return found_element.text.strip()
        return ""

    def get_profile(self, author_name: str) -> Dict[str, Any]:
        author_query = author_name.replace(" ", "+")
        url = f"http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300"

        response = requests.get(url)
        papers_list: List[Dict[str, Any]] = []

        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            entries = root.findall(f"{ATOM_NAMESPACE}entry")

            papers_list, papers_by_year = self._get_papers(entries, author_name)
            if len(papers_list) > 40:
                papers_list = self._select_papers(papers_by_year, author_name)
            
            # Trim the list to the 10 most recent papers
            papers_list = papers_list[:10]

            personal_info = "; ".join(
                [f"{details['Title & Abstract']}" for details in papers_list]
            )
            profile_info = summarize_research_direction_prompting(personal_info)
            return {"name": author_name, "profile": profile_info[0]}

        else:
            print("Failed to fetch data from arXiv.")
            return {"info": "fail!"}

    def _get_papers(self, entries: List[ElementTree.Element], author_name: str) -> Tuple[List[Dict[str, Any]], Dict[int, List[ElementTree.Element]]]:
        papers_list: List[Dict[str, Any]] = []
        papers_by_year: Dict[int, List[ElementTree.Element]] = {}

        for entry in entries:
            title = self.find_text(entry, f"{ATOM_NAMESPACE}title")
            published = self.find_text(entry, f"{ATOM_NAMESPACE}published")
            abstract = self.find_text(entry, f"{ATOM_NAMESPACE}summary")
            authors_elements = entry.findall(f"{ATOM_NAMESPACE}author")
            authors = [
                self.find_text(author, f"{ATOM_NAMESPACE}name")
                for author in authors_elements
            ]
            link = self.find_text(entry, f"{ATOM_NAMESPACE}id")

            if author_name in authors:
                coauthors = [author for author in authors if author != author_name]
                coauthors_str = ", ".join(coauthors)

                papers_list.append(
                    {
                        "date": published,
                        "Title & Abstract": f"{title}; {abstract}",
                        "coauthors": coauthors_str,
                        "link": link,
                    }
                )

                published_date = published
                date_obj = datetime.datetime.strptime(
                    published_date, "%Y-%m-%dT%H:%M:%SZ"
                )
                year = date_obj.year
                if year not in papers_by_year:
                    papers_by_year[year] = []
                papers_by_year[year].append(entry)

        return papers_list, papers_by_year

    def _select_papers(self, papers_by_year: Dict[int, List[ElementTree.Element]], author_name: str) -> List[Dict[str, Any]]:
        papers_list: List[Dict[str, Any]] = []

        for cycle_start in range(min(papers_by_year), max(papers_by_year) + 1, 5):
            cycle_end = cycle_start + 4
            for year in range(cycle_start, cycle_end + 1):
                if year in papers_by_year:
                    selected_papers = papers_by_year[year][:2]
                    for paper in selected_papers:
                        title = self.find_text(
                            paper, f"{ATOM_NAMESPACE}title"
                        )
                        abstract = self.find_text(
                            paper, f"{ATOM_NAMESPACE}summary"
                        )
                        authors_elements = paper.findall(
                            f"{ATOM_NAMESPACE}author"
                        )
                        co_authors = [
                            self.find_text(
                                author, f"{ATOM_NAMESPACE}name"
                            )
                            for author in authors_elements
                            if self.find_text(
                                author, f"{ATOM_NAMESPACE}name"
                            )
                            != author_name
                        ]

                        papers_list.append(
                            {
                                "Author": author_name,
                                "Title & Abstract": f"{title}; {abstract}",
                                "Date Period": f"{year}",
                                "Cycle": f"{cycle_start}-{cycle_end}",
                                "Co_author": ", ".join(co_authors),
                            }
                        )
        return papers_list

    def communicate(self, message: Dict[str, str]) -> str:
        return communicate_with_multiple_researchers_prompting(message)[0]

    def read_paper(
        self, external_data: Dict[str, Dict[str, List[str]]], domain: str
    ) -> str:
        time_chunks_embed = {}
        dataset = external_data
        for time in dataset.keys():
            papers = dataset[time]["abstract"]
            papers_embedding = get_bert_embedding(papers)
            time_chunks_embed[time] = papers_embedding

        trend = summarize_research_field_prompting(
            profile=self.profile,
            keywords=[domain],
            dataset=dataset,
            data_embedding=time_chunks_embed,
        )  # trend
        trend_output = trend[0]
        return trend_output

    def find_collaborators(self, input: Dict[str, str], parameter: float =0.5, max_number: int =3) -> List[str]:
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
        self, external_data: Dict[str, Dict[str, List[str]]], domain: str
    ) -> List[str]:
        time_chunks_embed = {}
        dataset = external_data
        for time in dataset.keys():
            papers = dataset[time]["abstract"]
            papers_embedding = get_bert_embedding(papers)
            time_chunks_embed[time] = papers_embedding

        trends = summarize_research_field_prompting(
            profile=self.profile,
            keywords=[domain],
            dataset=dataset,
            data_embedding=time_chunks_embed,
        )  # trend
        ideas: List[str] = []
        for trend in trends:
            idea = generate_ideas_prompting(trend)[0]
            ideas.append(idea)

        return ideas

    def write_paper(self, input: List[str], external_data: Dict[str, Dict[str, List[str]]]) -> str:
        paper_abstract = write_paper_abstract_prompting(input, external_data)
        return paper_abstract[0]

    def review_paper(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        paper_review = review_paper_prompting(input, external_data)
        return paper_review[0]

    def make_review_decision(
        self, input: Dict[str, str], external_data: Dict[str, str]
    ) -> str:
        return "accept"
