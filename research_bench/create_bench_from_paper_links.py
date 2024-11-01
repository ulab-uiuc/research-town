import argparse
import re
from multiprocessing import Pool, cpu_count
from typing import Any, Dict, List, Tuple, Optional

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
        urls = [line.strip() for line in f if line.strip()]

    arxiv_ids = []
    for url in urls:
        match = re.search(r'arxiv\.org/abs/([^\s/]+)', url)
        if match:
            arxiv_id_str = match.group(1)
            arxiv_id = arxiv_id_str.split('v')[0]
            arxiv_ids.append(arxiv_id)
    return arxiv_ids


def process_single_arxiv_id(
    arxiv_id: str, config: Config
) -> Tuple[str, Dict[str, Any]]:
    paper_data = get_paper_data(arxiv_id)
    authors = paper_data['authors']
    title = paper_data['title']
    author_data = get_author_data(arxiv_id, authors, title, config)
    reference_proposal = get_proposal_from_paper(
        arxiv_id, paper_data['introduction'], config
    )

    return arxiv_id, {
        'paper_data': paper_data,
        'author_data': author_data,
        'reference_proposal': reference_proposal,
    }


def process_arxiv_ids_chunk(
    arxiv_ids_chunk: List[str], config: Config
) -> Dict[str, Dict[str, Any]]:
    """
    Processes a chunk of arXiv IDs in parallel.
    """
    benchmark_chunk = {}
    for arxiv_id in arxiv_ids_chunk:
        arxiv_id, data = process_single_arxiv_id(arxiv_id, config)
        benchmark_chunk[arxiv_id] = data
    return benchmark_chunk


def process_arxiv_ids(
    arxiv_ids: List[str], output: str, config: Config, num_processes: Optional[int] = None
) -> Dict[str, Any]:
    if num_processes is None:
        num_processes = max(1, cpu_count() - 1)

    if num_processes == 1:
        # Single-process mode
        benchmark = {}
        for arxiv_id in tqdm(arxiv_ids, desc='Processing arXiv IDs'):
            _, data = process_single_arxiv_id(arxiv_id, config)
            benchmark[arxiv_id] = data
        save_benchmark(benchmark, output)
        return benchmark
    else:
        # Multi-process mode
        chunk_size = len(arxiv_ids) // num_processes
        arxiv_ids_chunks = [
            arxiv_ids[i : i + chunk_size] for i in range(0, len(arxiv_ids), chunk_size)
        ]

        with Pool(processes=num_processes) as pool:
            results = pool.starmap(
                process_arxiv_ids_chunk, [(chunk, config) for chunk in arxiv_ids_chunks]
            )

        # Combine results from all processes
        benchmark = {}
        for result in results:
            benchmark.update(result)

        # Save combined benchmark data
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
        '--num_processes',
        type=int,
        default=None,
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
