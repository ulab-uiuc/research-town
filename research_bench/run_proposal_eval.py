import argparse
import json
import os
from multiprocessing import Lock, Pool
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from research_bench.eval import compute_proposal_metrics
from research_bench.proposal_writing import write_proposal
from research_bench.utils import load_benchmark
from research_town.configs import Config
from research_town.data import Profile
from research_town.utils.logger import logger
import random
from collections import defaultdict


def inference(
    paper_id: str,
    paper_data: Dict[str, Any],
    author_data: Dict[str, Any],
    ref_proposal: str,
    mode: str,
    config: Config,
) -> Tuple[Dict[str, str], Dict[str, float]]:
    profiles = [Profile(**data) for data in author_data.values()]
    ref_abstracts_full = []
    for ref in paper_data.get('references', []):
        if ref['abstract'] is None:
            continue
        else:
            ref_abstracts_full.append(ref['abstract'])
        '''
        if ref['reference_section'] is None or ref['abstract'] is None:
            continue
        reference_sections = [section.lower() for section in ref['reference_section']]

        exclude_signal = False
        for section in reference_sections:
            #if 'related work' in section:
            #    ref_abstracts_full.append(ref['abstract'])
            #    break
            #if 'introduction' in section:
            #    ref_abstracts_full.append(ref['abstract'])
            #    break
            #if 'introduction' in section or 'related work' in section:
            #    ref_abstracts_full.append(ref['abstract'])
            #    break

            #if 'related work' in section:
            #    exclude_signal = True
            #    break
            #elif 'introduction' in section:
            #    exclude_signal = True
            #    break

        #if exclude_signal is False:
        #    ref_abstracts_full.append(ref['abstract'])
        '''
    print(len(ref_abstracts_full))
    paper_title = paper_data['title']
    if mode == 'fake_research_town':
        gen_proposal, gen_proposals_each_agent = write_proposal(mode, profiles, ref_abstracts_full, config, paper_title)
    else:
        gen_proposal = write_proposal(mode, profiles, ref_abstracts_full, config, paper_title)

    if mode == 'fake_research_town':
        overall_metrics = defaultdict(list)
        # assert each agent gen proposal is the same
        for idx, gen_proposal in enumerate(gen_proposals_each_agent):
            metrics = compute_proposal_metrics(ref_proposal, gen_proposal)
            for metric, score in metrics.items():
                overall_metrics[metric + '_per_agent'].append(score)
        metrics = compute_proposal_metrics(ref_proposal, gen_proposal)
        for metric, score in metrics.items():
            overall_metrics[metric] = score
        results = {
            'paper_id': paper_id,
            'ref_proposal': ref_proposal,
            'gen_proposal': gen_proposal,
        }
        return results, overall_metrics
    else:
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
    results: Dict[str, Any], metrics: Dict[str, float], output_path: str, lock: Any
) -> None:
    with lock:
        with open(output_path, 'a') as f:
            json.dump({**results, **metrics}, f)
            f.write('\n')


def process_task(
    task: Tuple[str, Dict[str, Any], Dict[str, Any], str, str, Config],
) -> Tuple[Dict[str, Any], Dict[str, float]]:
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
            'research_town',
            'sakana_ai_scientist',
            'debug',
            'fake_research_town',
            'fake_research_town_twice',
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

    lock = Lock()
    with Pool(processes=args.num_processes) as pool:
        tasks = [
            (
                paper_id,
                data['paper_data'],
                data['author_data'],
                data['reference_proposal'],
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
            with lock:
                for metric, scores in metrics_summary.items():
                    scores.append(metrics.get(metric, 0))

    # Report average metrics
    for metric, scores in metrics_summary.items():
        if scores:
            average = sum(scores) / len(scores)
            logger.info(f"Average {metric.replace('_', ' ').upper()}: {average:.4f}")


if __name__ == '__main__':
    main()
