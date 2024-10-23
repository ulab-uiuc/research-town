import argparse
from typing import Any, Dict, List, Set

from tqdm import tqdm
from utils import (
    get_arxiv_ids_from_keyword,
    get_author_data,
    get_paper_data,
    get_proposal_from_paper,
    save_benchmark,
)

from research_town.configs import Config


def process_keywords(
    keywords: List[str],
    max_papers_per_keyword: int,
    output: str,
    config: Config,
) -> Dict[str, Any]:
    benchmark = {}
    existing_arxiv_ids: Set[str] = set()

    for keyword in keywords:
        print(f"Fetching papers for keyword: '{keyword}'")
        arxiv_ids = get_arxiv_ids_from_keyword(
            keyword, existing_arxiv_ids, max_papers_per_keyword
        )
        for arxiv_id in tqdm(arxiv_ids, desc=f"Processing papers for '{keyword}'"):
            if arxiv_id in existing_arxiv_ids:
                continue

            paper_data = get_paper_data(arxiv_id)
            authors = paper_data['authors']
            title = paper_data['title']
            author_data = get_author_data(arxiv_id, authors, title, config)
            reference_proposal = get_proposal_from_paper(
                arxiv_id, paper_data['introduction'], config
            )

            benchmark[paper_data['arxiv_id']] = {
                'paper_data': paper_data,
                'author_data': author_data,
                'reference_proposal': reference_proposal,
            }
            existing_arxiv_ids.add(arxiv_id)
            save_benchmark(benchmark, output)

    return benchmark


def parse_args() -> argparse.Namespace:
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


def main() -> None:
    args = parse_args()
    keywords = args.keywords
    config = Config('../configs')
    process_keywords(keywords, args.max_papers_per_keyword, args.output, config)


if __name__ == '__main__':
    main()
