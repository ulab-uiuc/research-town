from typing import List, Dict
from .utils import *
from .construct_relation_graph import *


class BaseResearchAgent(object):
    def __init__(self, name: str) -> None:
        self.profile = self.get_profile(name)
        self.memory: Dict[str, str] = {}

    def get_profile(self, author_name: str) -> Dict[str, str]:
        author_query = author_name.replace(" ", "+")
        url = f"http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300"  # Adjust max_results if needed

        response = requests.get(url)
        papers_list = []

        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")

            total_papers = 0
            data_to_save = []

            papers_by_year = {}

            for entry in entries:
                title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
                published = entry.find(
                    "{http://www.w3.org/2005/Atom}published"
                ).text.strip()
                abstract = entry.find(
                    "{http://www.w3.org/2005/Atom}summary"
                ).text.strip()
                authors_elements = entry.findall("{http://www.w3.org/2005/Atom}author")
                authors = [
                    author.find("{http://www.w3.org/2005/Atom}name").text
                    for author in authors_elements
                ]
                link = entry.find(
                    "{http://www.w3.org/2005/Atom}id"
                ).text.strip()  # Get the paper link

                # Check if the specified author is exactly in the authors list
                if author_name in authors:
                    # Remove the specified author from the coauthors list for display
                    coauthors = [author for author in authors if author != author_name]
                    coauthors_str = ", ".join(coauthors)

                    papers_list.append(
                        {
                            "date": published,
                            "Title & Abstract": f"{title}; {abstract}",
                            "coauthors": coauthors_str,
                            "link": link,  # Add the paper link to the dictionary
                        }
                    )
                authors_elements = entry.findall("{http://www.w3.org/2005/Atom}author")
                authors = [
                    author.find("{http://www.w3.org/2005/Atom}name").text
                    for author in authors_elements
                ]

                if author_name in authors:
                    # print(author_name)
                    # print(authors)
                    total_papers += 1
                    published_date = entry.find(
                        "{http://www.w3.org/2005/Atom}published"
                    ).text.strip()
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
                                title = paper.find(
                                    "{http://www.w3.org/2005/Atom}title"
                                ).text.strip()
                                abstract = paper.find(
                                    "{http://www.w3.org/2005/Atom}summary"
                                ).text.strip()
                                authors_elements = paper.findall(
                                    "{http://www.w3.org/2005/Atom}author"
                                )
                                co_authors = [
                                    author.find(
                                        "{http://www.w3.org/2005/Atom}name"
                                    ).text
                                    for author in authors_elements
                                    if author.find(
                                        "{http://www.w3.org/2005/Atom}name"
                                    ).text
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
            self.profile, domain, dataset, time_chunks_embed
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
    ) -> str:
        time_chunks_embed = {}
        dataset = external_data
        for time in dataset.keys():
            papers = dataset[time]["abstract"]
            papers_embedding = get_bert_embedding(papers)
            time_chunks_embed[time] = papers_embedding

        trend, paper_link = summarize_research_field(
            self.profile, domain, dataset, time_chunks_embed
        )  # trend
        idea = generate_ideas(trend)[0]  # idea

        return idea

    def write_paper(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return "writing paper"

    def review_paper(self, input: Dict[str, str], external_data: Dict[str, str]) -> str:
        return "review comments"

    def make_review_decision(
        self, input: Dict[str, str], external_data: Dict[str, str]
    ) -> str:
        return "accept"
