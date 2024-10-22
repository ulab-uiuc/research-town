import argparse
import json
import os
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from research_bench.proposal_eval import compute_metrics
from research_bench.proposal_writing import (
    write_predicted_proposal,
    write_reference_proposal,
)
from research_bench.utils import load_benchmark
from research_town.configs import Config
from research_town.utils.logger import logger


def inference(
    paper_id: str, paper_data: Dict[str, Any], mode: str, config: Config
) -> Tuple[Dict[str, str], Dict[str, float]]:
    arxiv_id = paper_data.get('arxiv_id', '')
    authors = [author for author in paper_data.get('authors', [])]
    title = paper_data.get('title', '')
    paper_intro = paper_data.get('introduction', '')
    ref_abstracts = [ref['abstract'] for ref in paper_data.get('references', [])]

    author_profiles = get_author_profiles(arxiv_id, authors, title, config)
    ref_proposal = write_reference_proposal(paper_intro, config)
    gen_proposal = write_predicted_proposal(
        mode, author_profiles, ref_abstracts, config
    )

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
    args = parser.parse_args()

    config = Config('../configs')
    dataset = load_papers(args.input_path, args.output_path)
    logger.info(f'Processing {len(dataset)} papers')

    metrics_summary: Dict[str, List[float]] = {
        metric: [] for metric in ['bleu', 'rouge_l', 'gpt_metric_score', 'bert_score']
    }

    for paper_id, paper_data in tqdm(dataset.items(), desc='Processing papers'):
        results, metrics = inference(paper_id, paper_data, args.mode, config)
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
