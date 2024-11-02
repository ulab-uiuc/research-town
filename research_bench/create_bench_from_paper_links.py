import argparse
import json
import os
import re
from multiprocessing import Pool, cpu_count
from typing import Any, Dict, List, Tuple
from functools import partial

from tqdm import tqdm
from utils import (
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


def process_single_arxiv_id(arxiv_id: str, config: Config) -> Dict[str, Any]:
    paper_data = get_paper_data(arxiv_id)
    return {
        'paper_data': paper_data,
        'author_data': get_author_data(
            arxiv_id, paper_data['authors'], paper_data['title'], config
        ),
        'reference_proposal': get_proposal_from_paper(
            arxiv_id, paper_data['introduction'], config
        ),
    }


def save_benchmark_data(data: Dict[str, Any], output: str) -> None:
    existing_data = {}
    if os.path.exists(output):
        with open(output, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    existing_data.update(data)
    save_benchmark(existing_data, output)


def process_chunk(arxiv_ids_chunk: List[str], config: Config) -> Dict[str, Any]:
    """Processes a chunk of arXiv IDs and returns the result."""
    return {
        arxiv_id: process_single_arxiv_id(arxiv_id, config)
        for arxiv_id in arxiv_ids_chunk
    }

def process_chunk_single(arxiv_id: str, config: Config) -> Tuple[str, Any]:
    """Processes a single arXiv ID and returns its data or an empty result if an error occurs."""
    try:
        data = process_single_arxiv_id(arxiv_id, config)
        return arxiv_id, data
    except ValueError as e:
        print(f"Error processing arXiv ID {arxiv_id}: {e}")
        return arxiv_id, None  # Return None to indicate an error


def process_arxiv_ids(arxiv_ids: List[str], output: str, config: Config, num_processes: int) -> None:
    arxiv_ids_chunks = [arxiv_ids[i: i + num_processes] for i in range(0, len(arxiv_ids), num_processes)]

    with tqdm(total=len(arxiv_ids_chunks), desc='Processing arXiv IDs') as pbar:
        for chunk in arxiv_ids_chunks:
            if num_processes == 1:
                chunk_data = process_chunk(chunk, config)
            else:
                with Pool(processes=num_processes) as pool:
                    results = pool.starmap(process_chunk_single, [(arxiv_id, config) for arxiv_id in chunk])
                    chunk_data = {arxiv_id: data for arxiv_id, data in results if data is not None}
            
            save_benchmark_data(chunk_data, output)
            pbar.update()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Process arXiv URLs.')
    parser.add_argument(
        '--input', required=True, help='Path to the input file containing arXiv URLs.'
    )
    parser.add_argument(
        '--output', default='./benchmark/crossbench.json', help='Output file path.'
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
    process_arxiv_ids(arxiv_ids, args.output, config, args.num_processes)


if __name__ == '__main__':
    main()
