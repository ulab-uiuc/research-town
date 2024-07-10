from arxiv import Client, Search
from beartype.typing import Any, Dict, List, Tuple
from tqdm import tqdm


def co_author_frequency(
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


def co_author_filter(co_authors: Dict[str, int], limit: int = 5) -> List[str]:
    co_author_list = sorted(co_authors.items(), key=lambda p: p[1], reverse=True)
    return [name for name, _ in co_author_list[:limit]]


def fetch_author_info(author: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    client = Client()
    papers_info = []
    co_authors: Dict[str, int] = {}
    search = Search(query=f'au:{author}', max_results=10)
    for result in tqdm(
        client.results(search), desc='Processing Author Papers', unit='Paper'
    ):
        if author not in ', '.join(author.name for author in result.authors):
            continue
        author_list = [author.name for author in result.authors]
        co_authors = co_author_frequency(author, author_list, co_authors)
        paper_info = {
            'url': result.entry_id,
            'title': result.title,
            'abstract': result.summary,
            'authors': ', '.join(author.name for author in result.authors),
            'published': str(result.published).split(' ')[0],
            'updated': str(result.updated).split(' ')[0],
            'primary_cat': result.primary_category,
            'cats': result.categories,
        }
        papers_info.append(paper_info)
    co_author_names = co_author_filter(co_authors, limit=10)
    return papers_info, co_author_names
