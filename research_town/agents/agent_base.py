import datetime
from typing import Any, Dict, List
from xml.etree import ElementTree

import requests

from ..utils.author_relation import bfs
from ..utils.paper_collection import get_bert_embedding
from .agent_prompting import (
    generate_ideas,
    summarize_research_direction,
    summarize_research_field,
    write_paper_abstract,
)


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
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")

            total_papers = 0
            papers_by_year: Dict[int, List[ElementTree.Element]] = {}

            for entry in entries:
                title = self.find_text(entry, "{http://www.w3.org/2005/Atom}title")
                published = self.find_text(
                    entry, "{http://www.w3.org/2005/Atom}published"
                )
                abstract = self.find_text(entry, "{http://www.w3.org/2005/Atom}summary")
                authors_elements = entry.findall("{http://www.w3.org/2005/Atom}author")
                authors = [
                    self.find_text(author, "{http://www.w3.org/2005/Atom}name")
                    for author in authors_elements
                ]
                link = self.find_text(entry, "{http://www.w3.org/2005/Atom}id")

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

                    total_papers += 1
                    published_date = published
                    date_obj = datetime.datetime.strptime(
                        published_date, "%Y-%m-%dT%H:%M:%SZ"
                    )
                    year = date_obj.year
                    if year not in papers_by_year:
                        papers_by_year[year] = []
                    papers_by_year[year].append(entry)

            if total_papers > 40:
                for cycle_start in range(
                    min(papers_by_year), max(papers_by_year) + 1, 5
                ):
                    cycle_end = cycle_start + 4
                    for year in range(cycle_start, cycle_end + 1):
                        if year in papers_by_year:
                            selected_papers = papers_by_year[year][:2]
                            for paper in selected_papers:
                                title = self.find_text(
                                    paper, "{http://www.w3.org/2005/Atom}title"
                                )
                                abstract = self.find_text(
                                    paper, "{http://www.w3.org/2005/Atom}summary"
                                )
                                authors_elements = paper.findall(
                                    "{http://www.w3.org/2005/Atom}author"
                                )
                                co_authors = [
                                    self.find_text(
                                        author, "{http://www.w3.org/2005/Atom}name"
                                    )
                                    for author in authors_elements
                                    if self.find_text(
                                        author, "{http://www.w3.org/2005/Atom}name"
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

            # Trim the list to the 10 most recent papers
            papers_list = papers_list[:10]

            personal_info = "; ".join(
                [f"{details['Title & Abstract']}" for details in papers_list]
            )
            info = summarize_research_direction(personal_info)
            return {"name": author_name, "profile": info[0]}

        else:
            print("Failed to fetch data from arXiv.")
            return {"info": "fail!"}

    def communicate(self, message: Dict[str, str]) -> str:
        return "hello"

    def read_paper(
        self, external_data: Dict[str, Dict[str, List[str]]], domain: str
    ) -> str:
        time_chunks_embed = {}
        dataset = external_data
        for time in dataset.keys():
            papers = dataset[time]["abstract"]
            papers_embedding = get_bert_embedding(papers)
            time_chunks_embed[time] = papers_embedding

        trend, paper_link = summarize_research_field(
            profile=self.profile,
            keywords=[domain],
            dataset=dataset,
            data_embedding=time_chunks_embed,
        )  # trend
        return trend[0]

    def find_collaborators(self, input: Dict[str, str]) -> List[str]:
        return ["Alice", "Bob", "Charlie"]

    def get_co_author_relationships(self, name: str, max_node: int):
        start_author = [name]
        graph, node_feat, edge_feat = bfs(author_list=start_author, node_limit=max_node)
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

        trends, paper_links = summarize_research_field(
            profile=self.profile,
            keywords=[domain],
            dataset=dataset,
            data_embedding=time_chunks_embed,
        )  # trend
        ideas: List[str] = []
        for trend in trends:
            idea = generate_ideas(trend)[0]
            ideas.append(idea)

        return ideas

    def write_paper(self, input: List[str], external_data: Dict[str, Dict[str, List[str]]]) -> str:
        paper_abstract = write_paper_abstract(input, external_data)
        return paper_abstract[0]

    def review_paper(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return "review comments"

    def make_review_decision(
        self, input: Dict[str, str], external_data: Dict[str, str]
    ) -> str:
        return "accept"
