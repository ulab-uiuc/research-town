from arxiv import Client, Search
from beartype.typing import Any, Dict, List, Tuple
from tqdm import tqdm


def coauthor_frequency(
    author: str, author_list: List[str], co_authors: Dict[str, int]
) -> Dict[str, int]:
    for i in author_list:
        if author.lower() == i.lower():
            continue
        if i in co_authors:
            co_authors[i] += 1
        else:
            co_authors[i] = 1
    return co_authors


def coauthor_filter(co_authors: Dict[str, int], limit: int = 5) -> List[str]:
    co_author_list = sorted(co_authors.items(), key=lambda p: p[1], reverse=True)
    return [name for name, _ in co_author_list[:limit]]


def collect_proposals_and_coauthors(
    author: str, paper_max_num: int = 10
) -> Tuple[List[Dict[str, Any]], List[str]]:
    client = Client()
    abstracts = []
    co_authors: Dict[str, int] = {}
    search = Search(query=f'au:{author}', max_results=10)
    for result in tqdm(
        client.results(search), desc=f"Collecting {author}'s papers", unit='Paper'
    ):
        if author not in ', '.join(author.name for author in result.authors):
            continue
        author_list = [author.name for author in result.authors]
        co_authors = coauthor_frequency(author, author_list, co_authors)
        abstract = result.summary.replace('\n', ' ')
        abstracts.append(abstract)
    co_author_names = coauthor_filter(co_authors, limit=10)
    return abstracts, co_author_names
