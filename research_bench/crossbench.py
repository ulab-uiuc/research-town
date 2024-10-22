import argparse
import re
from typing import Any, Dict, List, Set

from tqdm import tqdm
from utils import (
    get_author_data,
    get_paper_data,
    get_proposal_from_paper,
    save_benchmark,
)


def get_arxiv_ids(input: str) -> List[str]:
    with open(input, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    arxiv_ids = []
    for url in urls:
        match = re.search(r'arxiv\.org/abs/([^\s/]+)', url)
        if match:
            arxiv_ids.append(match.group(1))
    return arxiv_ids


def process_arxiv_ids(
    arxiv_ids: List[str],
    output: str,
    model: str,
) -> Dict[str, Any]:
    benchmark = {}
    existing_arxiv_ids: Set[str] = set()

    for arxiv_id in tqdm(arxiv_ids, desc='Processing arXiv IDs'):
        if arxiv_id in existing_arxiv_ids:
            continue

        paper_data = get_paper_data(arxiv_id)
        author_data = get_author_data(arxiv_id)
        reference_proposal = get_proposal_from_paper(
            arxiv_id, paper_data['introduction'], model
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
    parser = argparse.ArgumentParser(description='Process arXiv URLs.')
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to the input file containing arXiv URLs.',
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./benchmark/crossbench.json',
        help='Output file path.',
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-40-mini',
        help='Model name for the single agent test.',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    arxiv_ids = get_arxiv_ids(args.input)
    process_arxiv_ids(arxiv_ids, args.output, args.model)


if __name__ == '__main__':
    main()
