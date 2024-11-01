from beartype import beartype
from beartype.typing import Dict, List, Optional, Tuple, Union, Set
from semanticscholar import SemanticScholar

from .error_handler import api_calling_error_exponential_backoff
from .model_prompting import model_prompting
from .prompt_constructor import openai_format_prompt_construct


def coauthor_frequency(
    author_id: str, author_list: List[Dict[str, str]], co_authors: Dict[str, int]
) -> Dict[str, int]:
    for author in author_list:
        if author_id == author['authorId']:
            continue
        if author['name'] in co_authors:
            co_authors[author['name']] += 1
        else:
            co_authors[author['name']] = 1
    return co_authors


def coauthor_filter(co_authors: Dict[str, int], limit: int = 5) -> List[str]:
    co_author_list = sorted(co_authors.items(), key=lambda p: p[1], reverse=True)
    return [name for name, _ in co_author_list[:limit]]


@api_calling_error_exponential_backoff(retries=5, base_wait_time=1)
def match_author_ids(author: str, known_paper_titles: List[str]) -> Set[str]:
    matched_author_ids = set()
    semantic_client = SemanticScholar()
    search_results = semantic_client.search_author(author, fields=['papers.title'])

    for result in search_results:
        for paper in result['papers']:
            if paper['title'].lower() in [title.lower() for title in known_paper_titles]:
                matched_author_ids.add(result['authorId'])
    return matched_author_ids

@api_calling_error_exponential_backoff(retries=5, base_wait_time=1)
def get_paper_from_author_id(author_id: str, paper_max_num: int = 10) -> List[Dict[str, str]]:
    semantic_client = SemanticScholar()
    author_data = semantic_client.get_author(author_id, fields=['papers.title'])
    papers = author_data['papers'][:paper_max_num]
    return papers

def collect_publications_and_coauthors(
    author: str,
    known_paper_titles: List[str] = [],
    paper_max_num: int = 10,
    exclude_paper_titles: bool = True,
) -> Tuple[List[str], List[str], List[str]]:

    matched_author_ids = match_author_ids(author, known_paper_titles)

    if len(matched_author_ids) > 1:
        raise ValueError('Multiple authors found with matching paper titles.')
    elif len(matched_author_ids) == 0:
        raise ValueError('No authors found with matching paper titles.')
    else:
        author_id = matched_author_ids.pop()

    papers = get_paper_from_author_id(author_id, paper_max_num)

    paper_abstracts = []
    paper_titles = []
    for paper in papers:
        if not paper['abstract']:
            continue

        if exclude_paper_titles and paper['title'] in known_paper_titles:
            continue

        paper_authors = paper['authors']
        co_authors = coauthor_frequency(author_id, paper_authors, co_authors)
        paper_abstract = paper['abstract'].replace('\n', ' ')
        paper_title = paper['title']
        paper_abstracts.append(paper_abstract)
        paper_titles.append(paper_title)
    co_author_names = coauthor_filter(co_authors, limit=10)

    if len(paper_abstracts) < 1 or len(paper_titles) < 1:
        raise ValueError('No enough papers found with abstracts.')

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
