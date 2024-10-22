import argparse
import json
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from research_bench.proposal_eval import compute_metrics
from research_bench.proposal_writing import extract_reference_proposal, write_proposal
from research_bench.utils import load_benchmark, load_cache_item, write_cache_item
from research_town.utils.logger import logger
from research_town.utils.paper_collector import (
    get_paper_by_arxiv_id,
    get_paper_introduction,
    get_references,
)


def get_reference_proposal(
    args: argparse.Namespace, paper_key: str, paper_data: Dict[str, Any]
) -> str:
    ref_proposal = load_cache_item(args.cache_path, paper_key, 'ref_proposal')
    if isinstance(ref_proposal, str):
        return ref_proposal

    try:
        arxiv_id = paper_data.get('arxiv_id')
        paper = get_paper_by_arxiv_id(arxiv_id) if arxiv_id else None
        introduction = get_paper_introduction(paper) if paper else ''
        ref_proposal = extract_reference_proposal(introduction) if introduction else ''
        write_cache_item(args.cache_path, paper_key, 'ref_proposal', ref_proposal)
        return ref_proposal
    except Exception as e:
        raise ValueError(f'Failed to get reference proposal for {paper_key}: {e}')


def get_generated_proposal(
    args: argparse.Namespace,
    paper_key: str,
    paper_data: Dict[str, Any],
) -> str:
    gen_proposal = load_cache_item(args.cache_path, paper_key, 'gen_proposal')
    if isinstance(gen_proposal, str):
        return gen_proposal

    try:
        authors = [author['name'] for author in paper_data.get('authors', [])]
        title = paper_data.get('title', '')
        arxiv_id = paper_data.get('arxiv_id', '')
        references = get_references(arxiv_id)
        ref_intros = fetch_reference_intros(args, paper_key, references)

        gen_proposal = write_proposal(
            args.mode, authors, ref_intros, arxiv_id, exclude_paper_titles=[title]
        )
        write_cache_item(args.cache_path, paper_key, 'gen_proposal', gen_proposal)
        return gen_proposal
    except Exception as e:
        raise ValueError(f'Error generating proposal for {paper_key}: {e}')


def fetch_reference_intros(
    args: argparse.Namespace, paper_key: str, references: List[Dict[str, Any]]
) -> List[str]:
    cached_intros = load_cache_item(args.cache_path, paper_key, 'reference_intros')
    if isinstance(cached_intros, list):
        return cached_intros

    intros = []
    try:
        for ref in references:
            arxiv_id = ref.get('arxivId')
            if arxiv_id:
                ref_paper = get_paper_by_arxiv_id(arxiv_id)
                if ref_paper:
                    logger.info(
                        f'Fetching introduction for referenced paper: {arxiv_id}'
                    )
                    intro = get_paper_introduction(ref_paper)
                    if intro:
                        intros.append(intro)
        write_cache_item(args.cache_path, paper_key, 'reference_intros', intros)
        return intros
    except Exception as e:
        raise ValueError(f'Error fetching reference intros for {paper_key}: {e}')


def process_paper(
    args: argparse.Namespace,
    paper_key: str,
    paper_data: Dict[str, Any],
) -> Tuple[Dict[str, str], Dict[str, float]]:
    try:
        ref_proposal = get_reference_proposal(args, paper_key, paper_data)
        gen_proposal = get_generated_proposal(args, paper_key, paper_data)
        metrics = compute_metrics(ref_proposal, gen_proposal)
        results = {
            'paper_key': paper_key,
            'ref_proposal': ref_proposal,
            'gen_proposal': gen_proposal,
        }
        return results, metrics
    except Exception as e:
        raise ValueError(f'Error processing paper {paper_key}: {e}')


def skip_processed_papers(output_path: str, papers: Dict[str, Any]) -> Dict[str, Any]:
    with open(output_path, 'r', encoding='utf-8') as outfile:
        processed_paper_keys = [json.loads(line).get('paper_key') for line in outfile]
        for paper_key in papers.keys():
            if paper_key in processed_paper_keys:
                papers.pop(paper_key)
                logger.info(f'Skipping processed paper: {paper_key}')
    return papers


def main(args: argparse.Namespace) -> None:
    dataset = load_benchmark(args.input_path)
    dataset = skip_processed_papers(args.output_path, dataset)
    logger.info(f'Processing {len(dataset)} papers.')

    metrics_summary: Dict[str, List[float]] = {
        'bleu': [],
        'rouge_l': [],
        'gpt_metric_score': [],
        'bert_score': [],
    }

    for paper_key, paper_data in tqdm(dataset, desc='Processing papers'):
        results, metrics = process_paper(args, paper_key, paper_data)
        if results:
            with open(args.output_path, 'a', encoding='utf-8') as outfile:
                outfile.write(json.dumps({**results, **metrics}) + '\n')

            for key in metrics_summary.keys():
                metrics_summary[key].append(metrics.get(key, 0))
        else:
            logger.warning(f'Skipping paper {paper_key} due to processing failure.')

    for metric, scores in metrics_summary.items():
        average_score = sum(scores) / len(scores) if scores else 0.0
        logger.info(
            f"Average {metric.replace('_', ' ').upper()} score: {average_score:.4f}"
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_path', type=str, required=True, help='Path to the input JSON file.'
    )
    parser.add_argument(
        '--output_path', type=str, required=True, help='Path to the output JSONL file.'
    )
    parser.add_argument('--cache_path', type=str, help='Path to the cache JSONL file.')
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['author-only', 'citation-only', 'author-citation', 'textgnn'],
        help='Processing mode.',
    )
    args = parser.parse_args()
    main(args)
