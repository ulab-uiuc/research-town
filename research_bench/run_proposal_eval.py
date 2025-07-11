import argparse
import json
import os
from multiprocessing import Manager, Pool
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from research_bench.eval import compute_proposal_metrics
from research_bench.proposal_writing import write_proposal
from research_bench.utils import load_benchmark
from research_town.configs import Config
from research_town.data import Profile
from research_town.utils.logger import logger


def inference(
    paper_id: str,
    paper_data: Dict[str, Any],
    author_data: Dict[str, Any],
    ref_proposal: str,
    mode: str,
    config: Config,
) -> Tuple[Dict[str, str], Dict[str, float]]:
    profiles = [Profile(**data) for data in author_data.values()]
    ref_abstracts = [ref['abstract'] for ref in paper_data.get('references', [])]

    gen_proposal = write_proposal(mode, profiles, ref_abstracts, config)

    metrics = compute_proposal_metrics(ref_proposal, gen_proposal)
    results = {
        'paper_id': paper_id,
        'ref_proposal': ref_proposal,
        'gen_proposal': gen_proposal,
    }
    return results, metrics


def load_papers(input_path: str, output_path: str) -> Any:
    dataset = load_benchmark(input_path)

    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            processed_ids = {json.loads(line)['paper_id'] for line in f}
        return {k: v for k, v in dataset.items() if k not in processed_ids}

    return dataset


def save_results(
    results: Dict[str, Any],
    metrics: Dict[str, float],
    output_path: str,
    lock: Any,
    metrics_summary: Dict[str, List[float]],
) -> None:
    with lock:
        with open(output_path, 'a') as f:
            json.dump({**results, **metrics}, f)
            f.write('\n')

        # Update metrics summary
        for metric, score in metrics.items():
            if metric in metrics_summary:
                metrics_summary[metric].append(score)


def process_task(
    task: Tuple[
        str,
        Dict[str, Any],
        Dict[str, Any],
        str,
        str,
        Config,
        str,
        Any,
        Dict[str, List[float]],
    ],
) -> None:
    (
        paper_id,
        paper_data,
        author_data,
        ref_proposal,
        mode,
        config,
        output_path,
        lock,
        metrics_summary,
    ) = task
    results, metrics = inference(
        paper_id, paper_data, author_data, ref_proposal, mode, config
    )
    save_results(results, metrics, output_path, lock, metrics_summary)


def main() -> None:
    parser = argparse.ArgumentParser(description='Research Proposal Generator')
    parser.add_argument(
        '--input_path', type=str, required=True, help='Input JSON file path'
    )
    parser.add_argument(
        '--output_path', type=str, required=True, help='Output JSONL file path'
    )
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=[
            'zero_shot',
            'author_only',
            'citation_only',
            'author_citation',
            'textgnn',
            'sakana_ai_scientist',
        ],
        help='Processing mode',
    )
    parser.add_argument(
        '--config_path',
        type=str,
        default='../configs',
        help='Path to the configuration directory',
    )
    parser.add_argument(
        '--num_processes',
        type=int,
        default=8,
        help='Number of parallel processes to use',
    )
    args = parser.parse_args()

    config = Config(args.config_path)
    dataset = load_papers(args.input_path, args.output_path)
    logger.info(f'Processing {len(dataset)} papers')

    # Create a manager for shared objects
    manager = Manager()
    lock = manager.Lock()
    metrics_summary = manager.dict(
        {
            metric: manager.list()
            for metric in [
                'bleu',
                'rouge_l',
                'gpt_metric_score',
                'bert_score',
                'embedding_similarity',
            ]
        }
    )

    # Prepare tasks
    tasks = [
        (
            paper_id,
            data['paper_data'],
            data['author_data'],
            data['reference_proposal'],
            args.mode,
            config,
            args.output_path,
            lock,
            metrics_summary,
        )
        for paper_id, data in dataset.items()
    ]

    # Process tasks in parallel
    with Pool(processes=args.num_processes) as pool:
        # Using tqdm for progress bar
        list(
            tqdm(
                pool.imap_unordered(process_task, tasks),
                total=len(tasks),
                desc='Processing papers',
            )
        )

    # Convert managed lists to regular lists for reporting
    local_metrics_summary = {
        metric: list(scores) for metric, scores in metrics_summary.items()
    }

    # Report average metrics
    for metric, scores in local_metrics_summary.items():
        if scores:
            average = sum(scores) / len(scores)
            logger.info(f"Average {metric.replace('_', ' ').upper()}: {average:.4f}")


if __name__ == '__main__':
    main()
