import argparse
import json
import os
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from research_bench.eval import compute_metrics
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

    metrics = compute_metrics(ref_proposal, gen_proposal)
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
    results: Dict[str, Any], metrics: Dict[str, float], output_path: str
) -> None:
    with open(output_path, 'a') as f:
        json.dump({**results, **metrics}, f)
        f.write('\n')


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
        choices=['author_only', 'citation_only', 'author_citation', 'textgnn'],
        help='Processing mode',
    )
    parser.add_argument(
        '--config_path',
        type=str,
        default='../configs',
        help='Path to the configuration directory',
    )
    args = parser.parse_args()

    config = Config(args.config_path)
    dataset = load_papers(args.input_path, args.output_path)
    logger.info(f'Processing {len(dataset)} papers')

    metrics_summary: Dict[str, List[float]] = {
        metric: [] for metric in ['bleu', 'rouge_l', 'gpt_metric_score', 'bert_score']
    }

    for paper_id, data in tqdm(dataset.items(), desc='Processing papers'):
        paper_data = data['paper_data']
        author_data = data['author_data']
        reference_proposal = data['reference_proposal']

        results, metrics = inference(
            paper_id, paper_data, author_data, reference_proposal, args.mode, config
        )
        save_results(results, metrics, args.output_path)

        for metric, scores in metrics_summary.items():
            scores.append(metrics.get(metric, 0))

    # Report average metrics
    for metric, scores in metrics_summary.items():
        if scores:
            average = sum(scores) / len(scores)
            logger.info(f"Average {metric.replace('_', ' ').upper()}: {average:.4f}")


if __name__ == '__main__':
    main()
