# common.py

import json
import os
import time
from typing import Any, Dict, List, Optional, Set

import arxiv
import requests

from research_town.utils.model_prompting import model_prompting

SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/'


def get_references(arxiv_id: str, max_retries: int = 5) -> List[Dict[str, Any]]:
    url = f'{SEMANTIC_SCHOLAR_API_URL}ARXIV:{arxiv_id}/references'
    params = {'limit': 100}
    headers = {'User-Agent': 'PaperProcessor/1.0'}

    for attempt in range(max_retries):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return [
                ref['citedPaper'] for ref in data.get('data', []) if 'citedPaper' in ref
            ]
        else:
            wait_time = 2**attempt
            print(
                f'Error {response.status_code} fetching references for {arxiv_id}. Retrying in {wait_time}s...'
            )
            time.sleep(wait_time)  # Exponential backoff
    print(f'Failed to fetch references for {arxiv_id} after {max_retries} attempts.')
    return []


def get_paper_by_keyword(
    keyword: str, existing_arxiv_ids: Set[str], max_papers: int = 10
) -> List[arxiv.Result]:
    query = f'all:"{keyword}" AND (cat:cs.AI OR cat:cs.LG)'
    search = arxiv.Search(
        query=query,
        max_results=max_papers * 2,  # Fetch extra to account for duplicates
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    papers = []
    for paper in search.results():
        short_id = paper.get_short_id()
        if short_id not in existing_arxiv_ids:
            papers.append(paper)
            existing_arxiv_ids.add(short_id)
        if len(papers) >= max_papers:
            break
    return papers


def save_benchmark(benchmark: Dict[str, Any], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark, f, indent=4, ensure_ascii=False)
    print(f'Benchmark saved to {output_path}')


def get_paper_by_arxiv_id(arxiv_id: str) -> Optional[arxiv.Result]:
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(search.results())
        return results[0] if results else None
    except Exception as e:
        print(f'Error fetching paper {arxiv_id}: {e}')
        return None


def process_paper(paper: arxiv.Result) -> Dict[str, Any]:
    arxiv_id = paper.get_short_id()
    references = get_references(arxiv_id)
    return {
        'title': paper.title,
        'arxiv_id': arxiv_id,
        'authors': [author.name for author in paper.authors],
        'abstract': paper.summary,
        'published': paper.published.isoformat(),
        'updated': paper.updated.isoformat(),
        'references': references,
    }