import datetime

import arxiv
import requests
from beartype.typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_daily_papers(
    query: str, max_results: int = 2
) -> Tuple[Dict[str, Dict[str, List[str]]], str]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = client.results(search)
    content: Dict[str, Dict[str, Any]] = {}
    for result in tqdm(results, desc=f'Collecting papers with "{query}"', unit='Paper'):
        paper_title = result.title
        paper_url = result.entry_id
        proposal = result.summary.replace('\n', ' ')
        paper_authors = [author.name for author in result.authors]
        paper_domain = result.primary_category
        publish_time = result.published.date()
        paper_timestamp = int(
            datetime.datetime(
                publish_time.year, publish_time.month, publish_time.day
            ).timestamp()
        )
        (
            paper_section_contents,
            paper_table_captions,
            paper_figure_captions,
            paper_bibliography,
        ) = get_paper_content(paper_url)

        if publish_time in content:
            content[publish_time]['title'].append(paper_title)
            content[publish_time]['abstract'].append(proposal)
            content[publish_time]['authors'].append(paper_authors)
            content[publish_time]['url'].append(paper_url)
            content[publish_time]['domain'].append(paper_domain)
            content[publish_time]['timestamp'].append(paper_timestamp)
            content[publish_time]['section_contents'].append(paper_section_contents)
            content[publish_time]['table_captions'].append(paper_table_captions)
            content[publish_time]['figure_captions'].append(paper_figure_captions)
            content[publish_time]['bibliography'].append(paper_bibliography)
        else:
            content[publish_time] = {}
            content[publish_time]['title'] = [paper_title]
            content[publish_time]['abstract'] = [proposal]
            content[publish_time]['authors'] = [paper_authors]
            content[publish_time]['url'] = [paper_url]
            content[publish_time]['domain'] = [paper_domain]
            content[publish_time]['timestamp'] = [paper_timestamp]
            content[publish_time]['section_contents'] = [paper_section_contents]
            content[publish_time]['table_captions'] = [paper_table_captions]
            content[publish_time]['figure_captions'] = [paper_figure_captions]
            content[publish_time]['bibliography'] = [paper_bibliography]
    return content, publish_time


def get_paper_content(
    url: str,
) -> Tuple[
    Optional[Dict[str, str]],
    Optional[Dict[str, str]],
    Optional[Dict[str, str]],
    Optional[Dict[str, str]],
]:
    section_contents = None
    table_captions = None
    figure_captions = None
    bibliography = None
    html_url = url.replace('abs', 'html')
    try:
        response = requests.get(html_url, timeout=60)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            article = soup.find('article', class_='ltx_document')

            # section contents
            sections = article.find_all('section', class_='ltx_section')
            sections.extend(article.find_all('section', class_='ltx_appendix'))
            if len(sections) > 0:
                section_contents = {}
                for section in sections:
                    section_tag_raw = section.find(
                        attrs={
                            'class': [
                                'ltx_title ltx_title_section',
                                'ltx_title ltx_title_appendix',
                            ]
                        }
                    )
                    if section_tag_raw:
                        section_tag = section_tag_raw.text.replace('\n', '')
                    else:
                        continue
                    section_content = section.text
                    section_contents[section_tag] = section_content

            # bibliography
            bibliography_raw = article.find('section', class_='ltx_bibliography')
            if bibliography_raw is not None:
                bibliography = {}
                bibliography_list = bibliography_raw.find_all(
                    'li', class_='ltx_bibitem'
                )
                for bibliography_item in bibliography_list:
                    bibliography_tag_raw = bibliography_item.find(
                        'span', class_='ltx_tag'
                    )
                    if bibliography_tag_raw:
                        bibliography_tag = bibliography_tag_raw.text
                    else:
                        continue
                    bibliography_content = bibliography_item.text
                    bibliography[bibliography_tag] = bibliography_content

            # figure captions
            figures = article.find_all('figure', class_='ltx_figure')
            if len(figures) > 0:
                figure_captions = {}
                figure_index = 0
                for figure in figures:
                    figure_caption_raw = figure.find_all(
                        'figcaption', class_='ltx_caption'
                    )
                    if len(figure_caption_raw) > 0:
                        figure_caption = figure_caption_raw[-1].text
                    else:
                        continue
                    figure_tag_raw = figure.find_all('span', class_='ltx_tag')
                    if len(figure_tag_raw) > 0:
                        figure_tag = figure_tag_raw[-1].text
                    else:
                        figure_index += 1
                        figure_tag = str(figure_index)
                    figure_captions[figure_tag] = figure_caption

            # table_captions
            tables = article.find_all('figure', class_='ltx_table')
            if len(tables) > 0:
                table_captions = {}
                table_index = 0
                for table in tables:
                    table_caption_raw = table.find('figcaption', class_='ltx_caption')
                    if table_caption_raw:
                        table_caption = table_caption_raw.text
                    else:
                        continue
                    table_tag_raw = table.find('span', class_='ltx_tag')
                    if table_tag_raw:
                        table_tag = table_tag_raw.text
                    else:
                        table_index += 1
                        table_tag = str(table_index)
                    table_captions[table_tag] = table_caption
    except requests.exceptions.RequestException:
        pass
    return section_contents, table_captions, figure_captions, bibliography


def get_intro(url: str) -> Optional[str]:
    contents = get_paper_content(url)
    if contents is None or contents[0] is None:
        return None
    section_contents = contents[0]
    for section_name, section_content in section_contents.items():
        if 'Introduction' in section_name:
            return section_content
    return None
