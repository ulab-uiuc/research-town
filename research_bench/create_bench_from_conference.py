import argparse
import json
import os
import re
from multiprocessing import Pool
from typing import Any, Dict, List, Tuple

from tqdm import tqdm
from utils import (
    get_all_reviews,
    get_author_data,
    get_paper_data,
    get_proposal_from_paper,
    save_benchmark,
)

from research_town.configs import Config


def get_arxiv_ids(input_file: str) -> List[str]:
    with open(input_file, 'r', encoding='utf-8') as f:
        arxiv_ids = []
        for line in f:
            line = line.strip()
            match = re.search(r'arxiv\.org/abs/([^\s/]+)', line)
            if match:
                arxiv_id = match.group(1).split('v')[0]
                arxiv_ids.append(arxiv_id)
        return arxiv_ids


def process_single_arxiv_id(
    arxiv_id: str, config: Config, reviews: Dict[str, Any]
) -> Tuple[str, Any]:
    """Processes a single arXiv ID, handling any errors gracefully."""
    try:
        paper_data = get_paper_data(arxiv_id)
        if arxiv_id not in reviews:
            # If reviews are not available, return None
            return arxiv_id, None

        return arxiv_id, {
            'paper_data': paper_data,
            'author_data': get_author_data(
                arxiv_id, paper_data['authors'], paper_data['title'], config
            ),
            'reference_proposal': get_proposal_from_paper(
                arxiv_id, paper_data['introduction'], config
            ),
            'reviews': reviews[arxiv_id]['reviews'],
        }
    except ValueError as e:
        print(f'Error processing arXiv ID {arxiv_id}: {e}')
        return arxiv_id, None  # Return None to indicate an error


def save_benchmark_data(data: Dict[str, Any], output: str) -> None:
    existing_data = {}
    if os.path.exists(output):
        with open(output, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    existing_data.update(data)
    save_benchmark(existing_data, output)


def process_arxiv_ids(
    arxiv_ids: List[str],
    reviews: Dict[str, Any],
    output: str,
    config: Config,
    include_reviews: bool,
    num_processes: int,
) -> None:
    chunk_size = max(1, len(arxiv_ids) // (num_processes * 4))
    arxiv_ids_chunks = [
        arxiv_ids[i : i + chunk_size] for i in range(0, len(arxiv_ids), chunk_size)
    ]

    with tqdm(total=len(arxiv_ids_chunks), desc='Processing arXiv IDs') as pbar:
        for chunk in arxiv_ids_chunks:
            if num_processes == 1:
                # Single-process mode
                results = [
                    process_single_arxiv_id(arxiv_id, config, reviews)
                    for arxiv_id in chunk
                ]
            else:
                # Multiprocessing mode
                with Pool(processes=num_processes) as pool:
                    results = pool.starmap(
                        process_single_arxiv_id,
                        [(arxiv_id, config, reviews) for arxiv_id in chunk],
                    )

                    pool.close()
                    pool.join()
            # Filter out None results and save data
            chunk_data = {
                arxiv_id: data for arxiv_id, data in results if data is not None
            }
            save_benchmark_data(chunk_data, output)
            pbar.update()


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
        '--num_processes',
        type=int,
        default=1,
        help='Number of processes to use. Set to 1 for single-process mode. Default is based on available CPU cores.',
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

    process_arxiv_ids(
        arxiv_ids, reviews, args.output, config, include_reviews, args.num_processes
    )


if __name__ == '__main__':
    main()
