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
from research_bench.utils import load_benchmark, with_cache
from research_town.configs import Config
from research_town.data import Profile
from research_town.dbs import ProfileDB
from research_town.utils.logger import logger
from research_town.utils.paper_collector import (
    get_paper_by_arxiv_id,
    get_paper_introduction,
    get_reference_introductions,
)


@with_cache('profile_cache')
def get_author_profiles(
    authors: List[str], title: str, config: Config
) -> List[Profile]:
    """Retrieve author biographies from the ProfileDB."""
    profile_db = ProfileDB()
    profile_db.pull_profiles(names=authors, config=config, exclude_paper_titles=[title])
    return [profile_db.get(name=author)[0] for author in authors]


@with_cache('paper_cache')
def get_reference_proposal(arxiv_id: str, config: Config) -> str:
    """Generate a reference proposal based on paper introduction."""
    try:
        paper = get_paper_by_arxiv_id(arxiv_id)
        if not paper:
            return ''
        introduction = get_paper_introduction(paper)
        return write_reference_proposal(introduction, config) if introduction else ''
    except Exception as e:
        logger.error(f'Failed to get reference proposal for {arxiv_id}: {e}')
        return ''


@with_cache('proposal_cache')
def get_predicted_proposal(
    arxiv_id: str, profiles: List[Profile], config: Config, mode: str
) -> str:
    """Generate a predicted proposal based on author profiles and references."""
    try:
        ref_intros = get_reference_introductions(arxiv_id)
        return write_predicted_proposal(mode, profiles, ref_intros, config)
    except Exception as e:
        logger.error(f'Error generating proposal for {arxiv_id}: {e}')
        return ''


def inference(
    paper_id: str, paper_data: Dict[str, Any], mode: str, config: Config
) -> Tuple[Dict[str, str], Dict[str, float]]:
    """Generate and evaluate proposals for a paper."""
    arxiv_id = paper_data.get('arxiv_id', '')
    authors = [author['name'] for author in paper_data.get('authors', [])]
    title = paper_data.get('title', '')

    # Get author profiles and generate proposals
    author_profiles = get_author_profiles(authors, title, config)
    ref_proposal = get_reference_proposal(arxiv_id, config)
    gen_proposal = get_predicted_proposal(arxiv_id, author_profiles, config, mode)

    if not ref_proposal or not gen_proposal:
        raise ValueError('Failed to generate proposals')

    # Compute metrics
    metrics = compute_metrics(ref_proposal, gen_proposal)
    results = {
        'paper_id': paper_id,
        'ref_proposal': ref_proposal,
        'gen_proposal': gen_proposal,
    }
    return results, metrics


def load_papers(input_path: str, output_path: str) -> Any:
    """Load papers from the dataset, excluding already processed papers."""
    dataset = load_benchmark(input_path)

    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            processed_ids = {json.loads(line)['paper_id'] for line in f}
        return {k: v for k, v in dataset.items() if k not in processed_ids}

    return dataset


def save_results(
    results: Dict[str, Any], metrics: Dict[str, float], output_path: str
) -> None:
    """Save results and metrics to the output file."""
    with open(output_path, 'a') as f:
        json.dump({**results, **metrics}, f)
        f.write('\n')


def main() -> None:
    """Main entry point for the research proposal generator."""
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
        choices=['author-only', 'citation-only', 'author-citation', 'textgnn'],
        help='Processing mode',
    )
    args = parser.parse_args()

    # Initialize configuration and load papers
    config = Config('../configs')
    dataset = load_papers(args.input_path, args.output_path)
    logger.info(f'Processing {len(dataset)} papers')

    # Process papers
    metrics_summary: Dict[str, List[float]] = {
        metric: [] for metric in ['bleu', 'rouge_l', 'gpt_metric_score', 'bert_score']
    }

    for paper_id, paper_data in tqdm(dataset.items(), desc='Processing papers'):
        try:
            results, metrics = inference(paper_id, paper_data, args.mode, config)
            save_results(results, metrics, args.output_path)

            for metric, scores in metrics_summary.items():
                scores.append(metrics.get(metric, 0))
        except Exception as e:
            logger.warning(f'Failed to process paper {paper_id}: {e}')

    # Report average metrics
    for metric, scores in metrics_summary.items():
        if scores:
            average = sum(scores) / len(scores)
            logger.info(f"Average {metric.replace('_', ' ').upper()}: {average:.4f}")


if __name__ == '__main__':
    main()
