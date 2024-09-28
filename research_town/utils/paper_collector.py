import re
from io import BytesIO

import arxiv
import requests
from beartype.typing import Dict, List, Optional
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from tqdm import tqdm

from ..dbs.data import Paper


def get_related_paper(query: str, num_results: int, domain: Optional[str]) -> List[Paper]:
    if domain is None:
        arxiv_query = query
    arxiv_query = f'({query}) AND cat:{domain}'

    search = arxiv.Search(
        query=arxiv_query,
        max_results=num_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    papers_list = []

    for result in search.results():
        paper = Paper(
            title=result.title,
            abstract=result.summary,
            authors=[author.name for author in result.authors],
            url=result.entry_id,
            domain=domain,
            timestamp=int(result.published.timestamp()),
            sections=[],  # Sections not provided by arXiv API
            bibliography=[],  # Bibliography not provided by arXiv API
        )
        papers_list.append(paper)

    return papers_list


def get_recent_papers(domain: Optional[str] = None, max_results: int = 2) -> List[Paper]:
    if domain is None:
        arxiv_query = f'cat:cs'
    else:
        arxiv_query = f'cat:{domain}'
    client = arxiv.Client()
    search = arxiv.Search(
        query=arxiv_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    results = client.results(search)
    papers_list = []

    for result in tqdm(
        results, desc=f'Collecting recent papers in "{domain}"', unit='Paper'
    ):
        paper_title = result.title
        paper_url = result.entry_id
        paper_abstract = result.summary.replace('\n', ' ')
        paper_authors = [author.name for author in result.authors]
        paper_domain = result.primary_category
        publish_time = result.published
        paper_timestamp = int(publish_time.timestamp())

        # Get sections and bibliography if implemented
        paper_sections = get_paper_content_from_html(paper_url)
        paper_bibliography = get_paper_bibliography_from_html(paper_url)

        paper = Paper(
            title=paper_title,
            abstract=paper_abstract,
            authors=paper_authors,
            url=paper_url,
            domain=paper_domain,
            timestamp=paper_timestamp,
            sections=paper_sections,
            bibliography=paper_bibliography,
        )
        papers_list.append(paper)

    return papers_list


def fetch_html_content(url: str) -> Optional[BeautifulSoup]:
    if 'arxiv' not in url:
        return None
    elif 'abs' in url:
        html_url = url.replace('abs', 'html')
    elif 'pdf' in url:
        html_url = url.replace('pdf', 'html')
    else:
        html_url = url

    try:
        response = requests.get(html_url, timeout=60)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'lxml')
    except Exception:
        return None
    return None


def get_section_contents(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    section_contents = None
    article = soup.find('article', class_='ltx_document')
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
    return section_contents


def get_table_captions(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    table_captions = None
    article = soup.find('article', class_='ltx_document')
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
    return table_captions


def get_figure_captions(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    figure_captions = None
    article = soup.find('article', class_='ltx_document')
    figures = article.find_all('figure', class_='ltx_figure')

    if len(figures) > 0:
        figure_captions = {}
        figure_index = 0
        for figure in figures:
            figure_caption_raw = figure.find_all('figcaption', class_='ltx_caption')
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
    return figure_captions


def get_bibliography(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    bibliography = None
    article = soup.find('article', class_='ltx_document')
    bibliography_raw = article.find('section', class_='ltx_bibliography')

    if bibliography_raw is not None:
        bibliography = {}
        bibliography_list = bibliography_raw.find_all('li', class_='ltx_bibitem')
        for bibliography_item in bibliography_list:
            bibliography_tag_raw = bibliography_item.find('span', class_='ltx_tag')
            if bibliography_tag_raw:
                bibliography_tag = bibliography_tag_raw.text
            else:
                continue
            bibliography_content = bibliography_item.text
            bibliography[bibliography_tag] = bibliography_content
    return bibliography


def get_paper_content_from_html(url: str) -> Optional[Dict[str, str]]:
    soup = fetch_html_content(url)
    if soup is None:
        return None

    section_contents = get_section_contents(soup)
    return section_contents


def get_paper_figure_captions_from_html(url: str) -> Optional[Dict[str, str]]:
    soup = fetch_html_content(url)
    if soup is None:
        return None

    figure_captions = get_figure_captions(soup)
    return figure_captions


def get_paper_table_captions_from_html(url: str) -> Optional[Dict[str, str]]:
    soup = fetch_html_content(url)
    if soup is None:
        return None

    table_captions = get_table_captions(soup)
    return table_captions


def get_paper_bibliography_from_html(url: str) -> Optional[Dict[str, str]]:
    soup = fetch_html_content(url)
    if soup is None:
        return None

    bibliography = get_bibliography(soup)
    return bibliography


def get_paper_content_from_pdf(url: str) -> Optional[Dict[str, str]]:
    if 'abs' in url:
        pdf_url = url.replace('abs', 'pdf')
    elif 'html' in url:
        pdf_url = url.replace('html', 'pdf')
    else:
        pdf_url = url

    response = requests.get(pdf_url)
    file_stream = BytesIO(response.content)
    reader = PdfReader(file_stream)

    text = ''
    for page in reader.pages:
        text += page.extract_text()

    if text == '':
        return None

    section_titles = [
        'Abstract',
        'Introduction',
        'Related Work',
        'Background',
        'Methods',
        'Experiments',
        'Results',
        'Discussion',
        'Conclusion',
        'Conclusions',
        'Acknowledgments',
        'References',
        'Appendix',
        'Materials and Methods',
    ]

    section_pattern = re.compile(
        r'\b(' + '|'.join(re.escape(title) for title in section_titles) + r')\b',
        re.IGNORECASE,
    )

    sections = {}
    matches = list(section_pattern.finditer(text))

    for i, match in enumerate(matches):
        section_name = match.group()
        section_start = match.start()

        if i + 1 < len(matches):
            section_end = matches[i + 1].start()
        else:
            section_end = len(text)

        section_content = text[section_start:section_end].strip()
        sections[section_name] = section_content

    return sections


def get_paper_introduction(url: str) -> Optional[str]:
    sections = get_paper_content_from_html(url)
    if not sections:
        sections = get_paper_content_from_pdf(url)
    if not sections:
        return None
    for section_name, section_content in sections.items():
        if 'Introduction' in section_name:
            return section_content
    return section_content
