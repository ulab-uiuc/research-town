# script_1.py

import argparse
from typing import Any, Dict, List, Set

from tqdm import tqdm
from utils import get_paper_by_keyword, process_paper, save_benchmark


def process_keywords(
    keywords: List[str],
    max_papers_per_keyword: int,
    output: str,
) -> Dict[str, Any]:
    benchmark = {}
    existing_arxiv_ids: Set[str] = set()

    for keyword in keywords:
        print(f"Fetching papers for keyword: '{keyword}'")
        papers = get_paper_by_keyword(
            keyword, existing_arxiv_ids, max_papers_per_keyword
        )

        for paper in tqdm(papers, desc=f"Processing papers for '{keyword}'"):
            paper_data = process_paper(paper)
            benchmark[paper_data['arxiv_id']] = paper_data

            save_benchmark(benchmark, output)
    return benchmark


def parse_args():
    parser = argparse.ArgumentParser(description='Create an AI paper benchmark.')
    parser.add_argument(
        '--keywords',
        type=str,
        nargs='+',
        default=[
            'reinforcement learning',
            'large language model',
            'diffusion model',
            'graph neural network',
            'deep learning',
            'representation learning',
            'transformer',
            'federated learning',
            'generative model',
            'self-supervised learning',
            'vision language model',
            'explainable AI',
            'automated machine learning',
        ],
        help='List of keywords to search for.',
    )
    parser.add_argument(
        '--max_papers_per_keyword',
        type=int,
        default=10,
        help='Maximum number of papers per keyword.',
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./benchmark/mlbench.json',
        help='Output file path.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    keywords = args.keywords
    process_keywords(keywords, args.max_papers_per_keyword, args.output)


if __name__ == '__main__':
    main()
