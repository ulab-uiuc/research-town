import argparse
import json
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from research_bench.proposal_eval import compute_metrics
from research_bench.proposal_writing import extract_reference_proposal, write_proposal
from research_bench.utils import load_cache_item, write_cache_item
from research_town.utils.logger import logger
from research_town.utils.paper_collector import (
    get_paper_by_arxiv_id,
    get_paper_introduction,
    get_references,
)


def get_reference_proposal(
    args: argparse.Namespace, paper_key: str, paper_data: Dict[str, Any]
) -> Optional[str]:
    ref_proposal = load_cache_item(args.cache_path, paper_key, 'ref_proposal')
    if ref_proposal:
        return ref_proposal

    try:
        arxiv_id = paper_data.get('arxiv_id')
        paper = get_paper_by_arxiv_id(arxiv_id)
        introduction = get_paper_introduction(paper)
        ref_proposal = extract_reference_proposal(introduction)
        write_cache_item(args.cache_path, paper_key, 'ref_proposal', ref_proposal)
        return ref_proposal
    except Exception as e:
        logger.warning(f'Failed to get reference proposal for {paper_key}: {e}')
        return None


def get_generated_proposal(
    args: argparse.Namespace,
    paper_key: str,
    paper_data: Dict[str, Any],
    intros: List[str],
    paper_id: int,
) -> Optional[str]:
    gen_proposal = load_cache_item(args.cache_path, paper_key, 'gen_proposal')
    if gen_proposal:
        return gen_proposal

    try:
        authors = [author['name'] for author in paper_data.get('authors', [])]
        keyword = paper_data.get('keyword', '')
        title = paper_data.get('title', '')
        arxiv_id = paper_data.get('arxiv_id')
        references = get_references(arxiv_id)
        intros = fetch_reference_intros(args, paper_key, references)

        gen_proposal = write_proposal(
            args.mode, authors, intros, keyword, paper_id, exclude_titles=[title]
        )
        write_cache_item(args.cache_path, paper_key, 'gen_proposal', gen_proposal)
        return gen_proposal
    except Exception as e:
        logger.warning(f'Failed to generate proposal for {paper_key}: {e}')
        return None


def fetch_reference_intros(
    args: argparse.Namespace, paper_key: str, references: List[Dict[str, Any]]
) -> List[str]:
    cached_intros = load_cache_item(args.cache_path, paper_key, 'reference_intros')
    if cached_intros:
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
                    intros.append(intro)
        write_cache_item(args.cache_path, paper_key, 'reference_intros', intros)
    except Exception as e:
        logger.warning(f'Error fetching references for {paper_key}: {e}')
    return intros


def process_paper(
    args: argparse.Namespace,
    paper_key: str,
    paper_data: Dict[str, Any],
    paper_id: int,
) -> Optional[Dict[str, Any]]:
    try:
        ref_proposal = get_reference_proposal(args, paper_key, paper_data)
        if not ref_proposal:
            return None

        gen_proposal = get_generated_proposal(args, paper_key, paper_data, paper_id)
        if not gen_proposal:
            return None

        metrics = compute_metrics(ref_proposal, gen_proposal)

        return {
            'paper_key': paper_key,
            'ref_proposal': ref_proposal,
            'gen_proposal': gen_proposal,
            **metrics,
        }
    except Exception as e:
        logger.warning(f'Error processing paper {paper_key}: {e}')
        return None


def load_input_data(input_path: str) -> Dict[str, Any]:
    with open(input_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def skip_processed_papers(output_path: str, papers: List[str]) -> List[str]:
    try:
        with open(output_path, 'r', encoding='utf-8') as outfile:
            processed_count = sum(1 for _ in outfile)
            logger.info(f'Skipping {processed_count} already processed papers.')
            return papers[processed_count:]
    except Exception:
        return papers


def main(args: argparse.Namespace) -> None:
    data = load_input_data(args.input_path)
    papers = skip_processed_papers(args.output_path, list(data.keys()))
    logger.info(f'Processing {len(papers)} papers.')

    metrics_summary = {
        'bleu': [],
        'rouge_l': [],
        'gpt_metric_score': [],
        'bert_score': [],
    }

    for paper_id, paper_key in enumerate(
        tqdm(papers, desc='Processing papers'), start=1
    ):
        paper_data = data[paper_key]
        evaluation = process_paper(args, paper_key, paper_data, paper_id)
        if evaluation:
            with open(args.output_path, 'a', encoding='utf-8') as outfile:
                outfile.write(json.dumps(evaluation) + '\n')

            for key in metrics_summary.keys():
                metrics_summary[key].append(evaluation.get(key, 0.0))
        else:
            logger.warning(f'Skipping paper {paper_key} due to processing failure.')

    for metric, scores in metrics_summary.items():
        average_score = sum(scores) / len(scores) if scores else 0.0
        logger.info(
            f"Average {metric.replace('_', ' ').upper()} score: {average_score:.4f}"
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process research papers and compute evaluation metrics.'
    )
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
