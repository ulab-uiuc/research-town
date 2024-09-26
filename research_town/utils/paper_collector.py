import datetime
import re
from io import BytesIO

import arxiv
import requests
from beartype.typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
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
        paper_sections = get_paper_content_from_html(paper_url)
        paper_bibliography = get_paper_bibliography_from_html(paper_url)

        if publish_time in content:
            content[publish_time]['title'].append(paper_title)
            content[publish_time]['abstract'].append(proposal)
            content[publish_time]['authors'].append(paper_authors)
            content[publish_time]['url'].append(paper_url)
            content[publish_time]['domain'].append(paper_domain)
            content[publish_time]['timestamp'].append(paper_timestamp)
            content[publish_time]['sections'].append(paper_sections)
            content[publish_time]['bibliography'].append(paper_bibliography)
        else:
            content[publish_time] = {}
            content[publish_time]['title'] = [paper_title]
            content[publish_time]['abstract'] = [proposal]
            content[publish_time]['authors'] = [paper_authors]
            content[publish_time]['url'] = [paper_url]
            content[publish_time]['domain'] = [paper_domain]
            content[publish_time]['timestamp'] = [paper_timestamp]
            content[publish_time]['sections'] = [paper_sections]
            content[publish_time]['bibliography'] = [paper_bibliography]
    return content, publish_time


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
    sections = get_paper_content_from_pdf(url)
    if not sections:
        return None
    for section_name, section_content in sections.items():
        if 'Introduction' in section_name:
            return section_content
    return None
