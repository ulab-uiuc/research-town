import datetime
from xml.etree import ElementTree

import arxiv
import requests
import torch
from beartype.typing import Any, Dict, List, Tuple

from .retriever import get_embedding

ATOM_NAMESPACE = '{http://www.w3.org/2005/Atom}'


def get_related_papers(corpus: List[str], query: str, num: int) -> List[str]:
    corpus_embedding = get_embedding(corpus)
    query_embedding = get_embedding([query])
    indices = neighborhood_search(corpus_embedding, query_embedding, num)
    related_papers = [corpus[idx] for idx in indices[0]]
    return related_papers


def neighborhood_search(
    query_data: List[torch.Tensor], corpus_data: List[torch.Tensor], num: int
) -> List[List[int]]:
    xq = torch.cat(query_data, 0)
    xb = torch.cat(corpus_data, 0)

    xq = torch.nn.functional.normalize(xq, p=2, dim=1)
    xb = torch.nn.functional.normalize(xb, p=2, dim=1)

    similarity = torch.mm(xq, xb.t())

    _, indices = torch.topk(similarity, num, dim=1, largest=True)
    list_of_list_indices: List[List[int]] = indices.tolist()
    return list_of_list_indices


def find_text(element: ElementTree.Element, path: str) -> str:
    found_element = element.find(path)
    if found_element is not None and found_element.text is not None:
        return found_element.text.strip()
    return ''


def get_daily_papers(
    query: str, max_results: int = 2
) -> Tuple[Dict[str, Dict[str, List[str]]], str]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = client.results(search)
    content: Dict[str, Dict[str, Any]] = {}
    newest_day = ''
    for result in results:
        paper_title = result.title
        paper_url = result.entry_id
        paper_abstract = result.summary.replace('\n', ' ')
        paper_authors = [author.name for author in result.authors]
        paper_domain = result.primary_category
        publish_time = result.published.date()
        timestamp = int(
            datetime.datetime(
                publish_time.year, publish_time.month, publish_time.day
            ).timestamp()
        )
        newest_day = publish_time
        if publish_time in content:
            content[publish_time]['title'].append(paper_title)
            content[publish_time]['abstract'].append(paper_abstract)
            content[publish_time]['authors'].append(paper_authors)
            content[publish_time]['url'].append(paper_url)
            content[publish_time]['domain'].append(paper_domain)
            content[publish_time]['timestamp'].append(timestamp)
        else:
            content[publish_time] = {}
            content[publish_time]['title'] = [paper_title]
            content[publish_time]['abstract'] = [paper_abstract]
            content[publish_time]['authors'] = [paper_authors]
            content[publish_time]['url'] = [paper_url]
            content[publish_time]['domain'] = [paper_domain]
            content[publish_time]['timestamp'] = [timestamp]
    return content, newest_day


def get_papers(
    entries: List[ElementTree.Element], author_name: str
) -> Tuple[List[Dict[str, Any]], Dict[int, List[ElementTree.Element]]]:
    papers_list: List[Dict[str, Any]] = []
    papers_by_year: Dict[int, List[ElementTree.Element]] = {}

    for entry in entries:
        title = find_text(entry, f'{ATOM_NAMESPACE}title')
        published = find_text(entry, f'{ATOM_NAMESPACE}published')
        abstract = find_text(entry, f'{ATOM_NAMESPACE}summary')
        authors_elements = entry.findall(f'{ATOM_NAMESPACE}author')
        authors = [
            find_text(author, f'{ATOM_NAMESPACE}name') for author in authors_elements
        ]
        link = find_text(entry, f'{ATOM_NAMESPACE}id')

        if author_name in authors:
            coauthors = [author for author in authors if author != author_name]
            coauthors_str = ', '.join(coauthors)

            papers_list.append(
                {
                    'date': published,
                    'Title & Abstract': f'{title}; {abstract}',
                    'coauthors': coauthors_str,
                    'link': link,
                }
            )

            published_date = published
            date_obj = datetime.datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ')
            year = date_obj.year
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(entry)

    return papers_list, papers_by_year


def select_papers(
    papers_by_year: Dict[int, List[ElementTree.Element]], author_name: str
) -> List[Dict[str, Any]]:
    papers_list: List[Dict[str, Any]] = []

    for cycle_start in range(min(papers_by_year), max(papers_by_year) + 1, 5):
        cycle_end = cycle_start + 4
        for year in range(cycle_start, cycle_end + 1):
            if year in papers_by_year:
                selected_papers = papers_by_year[year][:2]
                for paper in selected_papers:
                    title = find_text(paper, f'{ATOM_NAMESPACE}title')
                    abstract = find_text(paper, f'{ATOM_NAMESPACE}summary')
                    authors_elements = paper.findall(f'{ATOM_NAMESPACE}author')
                    co_authors = [
                        find_text(author, f'{ATOM_NAMESPACE}name')
                        for author in authors_elements
                        if find_text(author, f'{ATOM_NAMESPACE}name') != author_name
                    ]

                    papers_list.append(
                        {
                            'Author': author_name,
                            'Title & Abstract': f'{title}; {abstract}',
                            'Date Period': f'{year}',
                            'Cycle': f'{cycle_start}-{cycle_end}',
                            'Co_author': ', '.join(co_authors),
                        }
                    )
    return papers_list


def get_paper_list(author_name: str) -> List[Dict[str, Any]]:
    author_query = author_name.replace(' ', '+')
    url = f'http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300'

    response = requests.get(url)

    if response.status_code == 200:
        xml_content = response.content.decode('utf-8', errors='ignore')
        root = ElementTree.fromstring(xml_content)
        entries = root.findall(f'{ATOM_NAMESPACE}entry')

        papers_list, papers_by_year = get_papers(entries, author_name)
        if len(papers_list) > 40:
            papers_list = select_papers(papers_by_year, author_name)

        # Trim the list to the 10 most recent papers
        papers_list = papers_list[:10]
        return papers_list
    else:
        print('Failed to fetch data from arXiv.')
        return []
