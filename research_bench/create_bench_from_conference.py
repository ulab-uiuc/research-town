import argparse
import json
import os
import re
from typing import Any, Dict, List, Set

from tqdm import tqdm
from utils import (
    get_all_reviews,
    get_author_data,
    get_paper_data,
    get_proposal_from_paper,
)

from research_town.configs import Config


def get_arxiv_ids(input: str) -> List[str]:
    with open(input, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    arxiv_ids = []
    for url in urls:
        match = re.search(r'arxiv\.org/abs/([^\s/]+)', url)
        if match:
            arxiv_id_str = match.group(1)
            arxiv_id = arxiv_id_str.split('v')[0]
            arxiv_ids.append(arxiv_id)
    return arxiv_ids


def process_arxiv_ids(
    arxiv_ids: List[str],
    reviews: Dict[str, Any],
    output: str,
    config: Config,
    include_reviews: bool,
) -> Dict[str, Any]:
    benchmark = {}
    existing_arxiv_ids: Set[str] = set()

    for arxiv_id in tqdm(arxiv_ids, desc='Processing arXiv IDs'):
        if arxiv_id in existing_arxiv_ids:
            continue

        paper_data = get_paper_data(arxiv_id)
        authors = paper_data['authors']
        title = paper_data['title']
        author_data = get_author_data(arxiv_id, authors, title, config)
        reference_proposal = get_proposal_from_paper(
            arxiv_id, paper_data['introduction'], config
        )

        if include_reviews:
            if arxiv_id not in reviews:
                print(f'Review not found for arXiv ID {arxiv_id}, skipping...')
                continue
            review = reviews[arxiv_id]['reviews']
            benchmark[paper_data['arxiv_id']] = {
                'paper_data': paper_data,
                'author_data': author_data,
                'reference_proposal': reference_proposal,
                'reviews': review,
            }
        else:
            benchmark[paper_data['arxiv_id']] = {
                'paper_data': paper_data,
                'author_data': author_data,
                'reference_proposal': reference_proposal,
            }

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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    arxiv_ids = get_arxiv_ids(args.input)
    config = Config('../configs')

    if 'iclrbench' in args.input:
        include_reviews = True
        if os.path.exists('./iclrbench/iclr_reviews.json'):
            with open('./iclrbench/iclr_reviews.json', 'r') as f:
                reviews = json.load(f)
            print(f'Loaded {len(reviews)} reviews from ICRL 2024.')
        else:
            reviews = get_all_reviews('ICLR.cc/2024/Conference')
            with open('./iclrbench/iclr_reviews.json', 'w') as f:
                json.dump(reviews, f)
    else:
        include_reviews = False
        reviews = {}

    process_arxiv_ids(arxiv_ids, reviews, args.output, config, include_reviews)


if __name__ == '__main__':
    main()
