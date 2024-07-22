import datetime

import arxiv
import requests
from beartype.typing import Any, Dict, List, Tuple
from bs4 import BeautifulSoup


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

        html_url = paper_url.replace('abs', 'html')
        response = requests.get(html_url, timeout=60)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            article = soup.find('article', class_='ltx_document')
            sections = article.find_all('section', class_='ltx_section')
            bibliography = article.find('section', class_='ltx_bibliography')
            appendices = article.find_all('section', class_='ltx_appendix')
            figures = article.find_all('figure', class_='ltx_figure')
            figure_captions = [figure.find(
                'figcaption').text for figure in figures]
            tables = article.find_all('figure', class_='ltx_table')
            table_captions = [table.find(
                'figcaption').text for table in tables]
    return content, newest_day
