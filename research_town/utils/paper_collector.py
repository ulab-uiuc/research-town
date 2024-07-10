import datetime

import arxiv
from beartype.typing import Any, Dict, List, Tuple

ATOM_NAMESPACE = '{http://www.w3.org/2005/Atom}'


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
