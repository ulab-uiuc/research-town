import argparse
import json
import os
from multiprocessing import Lock, Pool
from typing import Any, Dict, List, Sequence, Tuple

from tqdm import tqdm

from research_bench.eval import compute_review_metrics
from research_bench.review_writing import write_review
from research_bench.utils import load_benchmark
from research_town.configs import Config
from research_town.data import Profile
from research_town.utils.logger import logger


def inference(
    paper_id: str,
    paper_data: Dict[str, Any],
    author_data: Dict[str, Any],
    reviewer_data: Dict[str, Any],
    full_content: Dict[str, Any],
    strengths: List[str],
    weaknesses: List[str],
    mode: str,
    config: Config,
) -> Tuple[Dict[str, Sequence[str]], Dict[str, List[float]]]:
    intro = paper_data.get('introduction', '')
    profiles = [Profile(**data) for data in author_data.values()]
    profiles_reviewers = [Profile(**data) for data in reviewer_data.values()]
    ref_abstracts = [ref['abstract'] for ref in paper_data.get('references', [])]

    generated_strength, generated_weakness, score = write_review(
        mode, intro, profiles, profiles_reviewers, full_content, ref_abstracts, config
    )

    metrics = compute_review_metrics(
        strengths, weaknesses, generated_strength, generated_weakness
    )
    results = {
        'paper_id': paper_id,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'generated_strength': generated_strength,
        'generated_weakness': generated_weakness,
        'generated_scores': score,
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
    results: Dict[str, Any], metrics: Dict[str, Any], output_path: str, lock: Any
) -> None:
    with lock:
        with open(output_path, 'a') as f:
            json.dump({**results, **metrics}, f)
            f.write('\n')


def process_task(
    task: Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], List[str], List[str], str, Config],
) -> Tuple[Dict[str, Sequence[str]], Dict[str, List[float]]]:
    return inference(*task)


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
            'research_town',
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
        default=os.cpu_count(),
        help='Number of parallel processes to use',
    )
    args = parser.parse_args()

    config = Config(args.config_path)
    dataset = load_papers(args.input_path, args.output_path)
    logger.info(f'Processing {len(dataset)} papers')

    metrics_summary: Dict[str, List[float]] = {
        metric: []
        for metric in [
            'bleu',
            'rouge_l',
            'gpt_metric_score',
            'bert_score',
            'embedding_similarity',
        ]
    }

    for paper_id, data in tqdm(dataset.items(), desc='Processing papers'):
        full_content = data['full_content']
        paper_data = data['paper_data']
        author_data = data['author_data']
        reviewer_data = data['reviewer_data']
        reference_review = data['reviews']
        strengths = [review.get('strengths', '') for review in reference_review]
        weaknesses = [review.get('weaknesses', '') for review in reference_review]

        results, metrics = inference(
            paper_id, paper_data, author_data, reviewer_data, full_content, strengths, weaknesses, args.mode, config
        )
        lock = Lock()
        save_results(results, metrics, args.output_path, lock)

    lock = Lock()
    with Pool(processes=args.num_processes) as pool:
        tasks = [
            (
                paper_id,
                data['paper_data'],
                data['author_data'],
                data['reviewer_data'],
                data['full_content'],
                [review.get('strengths', '') for review in data['reviews']],
                [review.get('weaknesses', '') for review in data['reviews']],
                args.mode,
                config,
            )
            for paper_id, data in dataset.items()
        ]
        for results, metrics in tqdm(
            pool.imap_unordered(process_task, tasks),
            total=len(tasks),
            desc='Processing papers',
        ):
            save_results(results, metrics, args.output_path, lock)
            # with lock:
            #     for metric, scores in metrics_summary.items():
            #         scores.append(metrics.get(metric, 0.0))

    # Report average metrics
    # for metric, scores in metrics_summary.items():
    #     if scores:
    #         average = sum(scores) / len(scores)
    #         logger.info(f"Average {metric.replace('_', ' ').upper()}: {average:.4f}")


if __name__ == '__main__':
    main()
