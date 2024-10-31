from beartype import beartype
from beartype.typing import Dict, List, Optional, Tuple, Union
from semanticscholar import SemanticScholar
from tqdm import tqdm

from .error_handler import api_calling_error_exponential_backoff
from .model_prompting import model_prompting
from .prompt_constructor import openai_format_prompt_construct


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


@api_calling_error_exponential_backoff(retries=5, base_wait_time=1)
def collect_publications_and_coauthors(
    author: str,
    known_paper_titles: List[str] = [],
    paper_max_num: int = 10,
    exclude_paper_titles: bool = True,
) -> Tuple[List[str], List[str], List[str]]:
    semantic_client = SemanticScholar()

    # Retrieve author ID from Semantic Scholar
    matched_author_ids = set()
    search_results = semantic_client.search_author(author, fields=['papers'])

    if known_paper_titles == []:
        if len(search_results) == 1:
            matched_author_ids = {search_results[0]['authorId']}
        else:
            raise ValueError('Need to provide known paper titles for multiple authors.')
    else:
        for result in search_results:
            for paper in result['papers']:
                if paper['title'].lower() in [
                    title.lower() for title in known_paper_titles
                ]:
                    matched_author_ids.add(result['authorId'])

    if len(matched_author_ids) > 1:
        raise ValueError('Multiple authors found with matching paper titles.')
    elif len(matched_author_ids) == 0:
        raise ValueError('No authors found with matching paper titles.')

    paper_abstracts = []
    paper_titles = []
    co_authors: Dict[str, int] = {}
    author_id = matched_author_ids.pop()
    author_data = semantic_client.get_author(
        author_id, fields=['papers.authors', 'papers.title', 'papers.abstract']
    )
    papers = author_data['papers'][:paper_max_num]
    for paper in tqdm(papers, desc='Processing papers', unit='paper'):
        if not paper['abstract']:
            continue

        if exclude_paper_titles and paper['title'] in known_paper_titles:
            continue

        paper_authors = [author['name'] for author in paper['authors']]
        if author not in ', '.join(author for author in paper_authors):
            continue

        co_authors = coauthor_frequency(author, paper_authors, co_authors)
        paper_abstract = paper['abstract'].replace('\n', ' ')
        paper_title = paper['title']
        paper_abstracts.append(paper_abstract)
        paper_titles.append(paper_title)
    co_author_names = coauthor_filter(co_authors, limit=10)
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
