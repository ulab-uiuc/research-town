import json
import os
import re
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import openreview

from research_town.configs import Config
from research_town.dbs import ProfileDB
from research_town.utils.model_prompting import model_prompting
from research_town.utils.paper_collector import (
    get_paper_by_arxiv_id,
    get_paper_by_keyword,
    get_paper_by_title,
    get_paper_introduction,
    get_references,
)


def save_benchmark(benchmark: Dict[str, Any], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark, f, indent=4, ensure_ascii=False)
    print(f'Benchmark saved to {output_path}')


def load_benchmark(input_path: str) -> Any:
    with open(input_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def with_cache(
    cache_dir: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(arxiv_id: str, *args: Any, **kwargs: Any) -> Any:
            if not cache_dir:
                return func(arxiv_id, *args, **kwargs)

            cache_path = Path(cache_dir) / f'{arxiv_id}.json'
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            if cache_path.exists():
                with cache_path.open('r') as f:
                    return json.load(f)

            result = func(arxiv_id, *args, **kwargs)
            with cache_path.open('w') as f:
                json.dump(result, f)

            return result

        return wrapper

    return decorator


@with_cache(cache_dir='paper_data')
def get_paper_data(arxiv_id: str) -> Dict[str, Any]:
    paper = get_paper_by_arxiv_id(arxiv_id)
    if paper:
        references = get_references(arxiv_id)
        abstract = paper.summary.replace('\n', ' ')
        url = paper.entry_id
        if url:
            introduction = get_paper_introduction(url)
            introduction = introduction.replace('\n', ' ') if introduction else None
        else:
            raise ValueError(f'Paper with arXiv ID {arxiv_id} has no URL.')
        return {
            'title': paper.title,
            'url': url,
            'arxiv_id': arxiv_id,
            'authors': [author.name for author in paper.authors],
            'abstract': abstract,
            'introduction': introduction,
            'references': references,
        }
    else:
        raise ValueError(f'Paper with arXiv ID {arxiv_id} not found.')


def get_arxiv_ids_from_keyword(
    keyword: str, existing_arxiv_ids: Set[str], max_papers_per_keyword: int
) -> List[str]:
    papers = get_paper_by_keyword(keyword, existing_arxiv_ids, max_papers_per_keyword)
    return [paper.get_short_id().split('v')[0] for paper in papers]


def get_arxiv_id_from_title(title: str) -> Optional[str]:
    paper = get_paper_by_title(title)
    if paper:
        return str(paper.get_short_id().split('v')[0])
    else:
        return None


def get_url_from_title(title: str) -> Optional[str]:
    paper = get_paper_by_title(title)
    if paper:
        return str(paper.entry_id)
    else:
        return None


@with_cache(cache_dir='reference_proposal_data')
def get_proposal_from_paper(arxiv_id: str, intro: str, config: Config) -> str:
    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is a high-level summarized insight of a research field Machine Learning.\n\n'
                'Here are the five core questions:\n\n'
                '[Question 1] - What is the problem?\n\n'
                'Formulate the specific research question you aim to address. Only output one question and do not include any more information.\n\n'
                '[Question 2] - Why is it interesting and important?\n\n'
                'Explain the broader implications of solving this problem for the research community.\n'
                'Discuss how such paper will affect the future research.\n'
                'Discuss how addressing this question could advance knowledge or lead to practical applications.\n\n'
                '[Question 3] - Why is it hard?\n\n'
                'Discuss the challenges and complexities involved in solving this problem.\n'
                'Explain why naive or straightforward approaches may fail.\n'
                'Identify any technical, theoretical, or practical obstacles that need to be overcome. MAKE IT CLEAR.\n\n'
                "[Question 4] - Why hasn't it been solved before?\n\n"
                'Identify gaps or limitations in previous research or existing solutions.\n'
                'Discuss any barriers that have prevented this problem from being solved until now.\n'
                'Explain how your approach differs from or improves upon prior work. MAKE IT CLEAR.\n\n'
                '[Question 5] - What are the key components of my approach and results?\n\n'
                'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use.\n'
                'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                f'Introduction:\n{intro}\n\n'
                'Please provide the five core questions contents based on the above introduction.'
            ),
        }
    ]
    proposal = model_prompting(config.param.base_llm, prompt)[0]
    return proposal


@with_cache(cache_dir='author_data')
def get_author_data(
    arxiv_id: str,
    authors: List[str],
    title: str,
    config: Config,
    with_year_limit: bool = False,
) -> Dict[str, Any]:
    if with_year_limit:
        before_year = int('20' + arxiv_id.split('.')[0][:2])
    else:
        before_year = None
    profile_db = ProfileDB(config.database)
    profile_pks = profile_db.pull_profiles(
        names=authors,
        config=config,
        known_paper_titles=[title],
        before_year=before_year,
    )
    author_data = {}
    for pk in profile_pks:
        author_data[pk] = profile_db.get(pk=pk)[0].model_dump()
    return author_data


def get_all_reviews(venue_id: str) -> Dict[str, Any]:
    client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')
    all_reviews = {}
    submissions = client.get_all_notes(
        content={'venueid': f'{venue_id}'}, details='replies'
    )
    print('Fetching reviews...')
    for submission in submissions:
        url = get_url_from_title(submission.content['title']['value'])
        if not url:
            continue
        match = re.search(r'arxiv\.org/abs/([^\s/]+)', url)
        if match:
            arxiv_id_str = match.group(1)
            arxiv_id = arxiv_id_str.split('v')[0]

        reviews = []
        for reply in submission.details['replies']:
            review_content = {}
            if 'summary' in reply['content']:
                for key, value in reply['content'].items():
                    review_content[key] = (
                        value['value']
                        if isinstance(value, dict) and 'value' in value
                        else value
                    )
                reviews.append(review_content)

        all_reviews[arxiv_id] = {'reviews': reviews}
    print(len(all_reviews), 'reviews fetched.')
    return all_reviews
