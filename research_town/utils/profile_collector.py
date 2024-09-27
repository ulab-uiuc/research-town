from arxiv import Client, Search
from beartype import beartype
from beartype.typing import Any, Dict, List, Optional, Tuple, Union
from tqdm import tqdm

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


def collect_publications_and_coauthors(
    author: str, paper_max_num: int = 10
) -> Tuple[List[Dict[str, Any]], List[str]]:
    client = Client()
    abstracts = []
    co_authors: Dict[str, int] = {}
    search = Search(query=f'au:{author}', max_results=paper_max_num)
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


@beartype
def write_bio_prompting(
    publication_info: str,
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
    template_input = {'publication_info': publication_info}
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
    publication_info: str,
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
    template_input = {'publication_info': publication_info}
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
