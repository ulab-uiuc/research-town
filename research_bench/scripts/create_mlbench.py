#!/usr/bin/env python3

import argparse
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Set, Union

import arxiv
import requests
from tqdm import tqdm

# ---------------------
# Configuration Section
# ---------------------

AI_KEYWORDS = [
    'reinforcement learning',
    'large language model',
    'diffusion model',
    'graph neural network',
    'deep learning',
    'representation learning',
    'transformer',
    'federate learning',
    'generative model',
    'self-supervised learning',
    'vision language model',
    'explainable ai',
    'automated machine learning',
]

# Semantic Scholar API configuration
SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/'

# Logging configuration
LOG_FILE = 'create_bench.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w',
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# ---------------------
# Helper Functions
# ---------------------


def fetch_papers_for_keyword(
    keyword: str, existing_arxiv_ids: Set[str], max_papers: int = 10
) -> List[arxiv.Result]:
    search_query = f'all:"{keyword}" AND (cat:cs.AI OR cat:cs.LG)'
    logging.info(f"Searching arXiv for keyword: '{keyword}' with query: {search_query}")

    search = arxiv.Search(
        query=search_query,
        max_results=max_papers * 5,  # Fetch extra to account for duplicates
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers = []
    for paper in search.results():
        if paper.get_short_id() not in existing_arxiv_ids:
            papers.append(paper)
            existing_arxiv_ids.add(paper.get_short_id())
            if len(papers) >= max_papers * 5:
                break

    logging.info(f"Fetched {len(papers)} papers for keyword: '{keyword}'")
    return papers


def fetch_references(
    arxiv_id: str, max_retry: int = 5
) -> Optional[List[Dict[str, Any]]]:
    if 'v' in arxiv_id:
        arxiv_id = arxiv_id.split('v')[0]
    url = f'{SEMANTIC_SCHOLAR_API_URL}ARXIV:{arxiv_id}/references'
    params: Dict[str, Union[int, str]] = {
        'limit': 100,
        'fields': 'title,abstract,year,venue,authors,externalIds,url,referenceCount,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy',
    }

    for attempt in range(1, max_retry + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                references = [
                    ref['citedPaper']
                    for ref in data.get('data', [])
                    if 'citedPaper' in ref
                ]
                return [process_reference(ref) for ref in references]
            else:
                logging.warning(
                    f'Attempt {attempt}: Failed to fetch references for ARXIV:{arxiv_id} - Status Code: {response.status_code}'
                )
        except requests.RequestException as e:
            logging.warning(
                f'Attempt {attempt}: Error fetching references for ARXIV:{arxiv_id} - {e}'
            )
        time.sleep(3)  # Wait before retrying

    logging.error(
        f'Failed to fetch references for ARXIV:{arxiv_id} after {max_retry} attempts.'
    )
    return None


def process_reference(ref: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'title': ref.get('title', ''),
        'abstract': ref.get('abstract', ''),
        'year': ref.get('year', 0),
        'venue': ref.get('venue', ''),
        'authors': [author.get('name', '') for author in ref.get('authors', [])],
        'externalIds': ref.get('externalIds', {}),
        'url': ref.get('url', ''),
        'referenceCount': ref.get('referenceCount', 0),
        'citationCount': ref.get('citationCount', 0),
        'influentialCitationCount': ref.get('influentialCitationCount', 0),
        'isOpenAccess': ref.get('isOpenAccess', False),
        'fieldsOfStudy': ref.get('fieldsOfStudy', []),
    }


def create_benchmark(
    keywords: List[str], max_papers_per_keyword: int = 10
) -> Dict[str, Any]:
    benchmark = {}
    existing_arxiv_ids: Set[str] = set()

    for keyword in keywords:
        papers = fetch_papers_for_keyword(
            keyword, existing_arxiv_ids, max_papers_per_keyword
        )
        paper_count_per_keyword = 0
        for paper in tqdm(
            papers, desc=f"Processing keyword: '{keyword}'", unit='paper'
        ):
            arxiv_id = paper.get_short_id()
            if not arxiv_id:
                logging.warning(
                    f"Paper '{paper.title}' does not have a valid arXiv ID. Skipping."
                )
                continue
            if paper.title in benchmark:
                logging.warning(
                    f"Paper '{paper.title}' already exists in the benchmark. Skipping."
                )
                continue
            authors = [author.name for author in paper.authors]
            references = fetch_references(arxiv_id)
            if references is None:
                logging.warning(
                    f"Failed to fetch references for paper: '{paper.title}'"
                )
                continue
            if len(references) == 0:
                logging.warning(f"No references found for paper: '{paper.title}'")
                continue
            paper_count_per_keyword += 1
            if paper_count_per_keyword > max_papers_per_keyword:
                break
            benchmark[paper.title] = {
                'paper_title': paper.title,
                'arxiv_id': arxiv_id,
                'keyword': keyword,
                'authors': authors,
                'references': references,
            }

    return benchmark


def save_benchmark(benchmark: Dict[str, Any], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark, f, ensure_ascii=False, indent=4)
    logging.info(f'Benchmark saved to {output_path}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Create a benchmark dataset of AI-related arXiv papers.'
    )

    parser.add_argument(
        '--max_papers_per_keyword',
        type=int,
        default=10,
        help='Number of papers to fetch per keyword (default: 10).',
    )

    parser.add_argument(
        '--output',
        type=str,
        default='./benchmark/benchmark.json',
        help='Path to save the benchmark JSON file (default: ./benchmark/benchmark.json).',
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logging.info('Starting benchmark creation...')
    logging.info(f'Max papers per keyword: {args.max_papers_per_keyword}')
    logging.info(f'Output path: {args.output}')

    benchmark = create_benchmark(
        keywords=AI_KEYWORDS,
        max_papers_per_keyword=args.max_papers_per_keyword,
    )

    save_benchmark(benchmark, args.output)
    logging.info('Benchmark creation completed successfully.')


if __name__ == '__main__':
    main()
