from beartype import beartype
from beartype.typing import Any, Dict, List, Optional, Set, Tuple, Union
from semanticscholar import SemanticScholar

from .error_handler import api_calling_error_exponential_backoff
from .model_prompting import model_prompting
from .prompt_constructor import openai_format_prompt_construct


def coauthor_frequency(
    author_id: str, author_list: List[Dict[str, str]], co_authors: Dict[str, int]
) -> Dict[str, int]:
    for author in author_list:
        co_author_id = author.get('authorId')
        co_author_name = author.get('name')
        if not co_author_id or not co_author_name or co_author_id == author_id:
            continue
        co_authors[co_author_name] = co_authors.get(co_author_name, 0) + 1
    return co_authors


def coauthor_filter(co_authors: Dict[str, int], limit: int = 5) -> List[str]:
    co_author_list = sorted(co_authors.items(), key=lambda p: p[1], reverse=True)
    return [name for name, _ in co_author_list[:limit]]


@api_calling_error_exponential_backoff(retries=5, base_wait_time=1)
def match_author_ids(
    author_name: str, known_paper_titles: Optional[List[str]] = None
) -> Set[str]:
    semantic_client = SemanticScholar()
    search_results = semantic_client.search_author(
        author_name,
        fields=['authorId', 'papers.title'],
        limit=100,
    )

    author_ids = set()
    if known_paper_titles is None:
        for result in search_results:
            author_id = result['authorId']
            author_ids.add(author_id)
    else:
        known_titles_lower = {title.lower() for title in known_paper_titles}
        for result in search_results:
            author_id = result['authorId']
            papers = result['papers']
            for paper in papers:
                if paper.get('title', '').lower() in known_titles_lower:
                    author_ids.add(author_id)
                    break

    if not author_ids:
        raise ValueError('No authors found with matching paper titles or name.')
    elif len(author_ids) > 1 and known_paper_titles:
        raise ValueError('Multiple authors found with matching paper titles.')

    return author_ids


@api_calling_error_exponential_backoff(retries=5, base_wait_time=1)
def get_papers_from_author_id(
    author_id: str, paper_max_num: int = 20
) -> List[Dict[str, Any]]:
    semantic_client = SemanticScholar()
    author_data: Dict[str, Any] = semantic_client.get_author(
        author_id,
        fields=[
            'papers.title',
            'papers.abstract',
            'papers.authors',
        ],
    )
    papers = author_data.get('papers', [])
    return papers[:paper_max_num] if isinstance(papers, list) else []


def collect_publications_and_coauthors(
    author: str,
    known_paper_titles: Optional[List[str]] = None,
    paper_max_num: int = 20,
    exclude_known: bool = True,
) -> Tuple[List[str], List[str], List[str]]:
    matched_author_ids = match_author_ids(author, known_paper_titles)
    author_id = matched_author_ids.pop()  # Only one author ID is expected

    papers = get_papers_from_author_id(author_id, paper_max_num)
    paper_abstracts = []
    paper_titles = []
    co_authors: Dict[str, int] = {}

    if known_paper_titles is not None:
        known_titles_lower = {title.lower() for title in known_paper_titles}

    for paper in papers:
        title = paper.get('title', '')
        if exclude_known and known_paper_titles and title.lower() in known_titles_lower:
            continue

        abstract = paper.get('abstract')
        if abstract:
            paper_abstracts.append(abstract.replace('\n', ' '))
            paper_titles.append(title)

        paper_authors = paper.get('authors', [])
        co_authors = coauthor_frequency(author_id, paper_authors, co_authors)

    if not paper_abstracts or not paper_titles:
        raise ValueError('Not enough papers found with abstracts.')

    co_author_names = coauthor_filter(co_authors, limit=100)

    return paper_abstracts, paper_titles, co_author_names


@beartype
def write_bio_prompting(
    pub_info: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    model_name: str,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    """
    Write bio based on personal research history
    """
    template_input = {'pub_info': pub_info}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    return model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]


@beartype
def summarize_domain_prompting(
    pub_info: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    model_name: str,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    """
    Check domain based on personal research history
    """
    template_input = {'pub_info': pub_info}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    domain_str = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
    domains = domain_str[0].split(';')
    return [domain.strip() for domain in domains]
