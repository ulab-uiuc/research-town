import argparse
import json
import os
from multiprocessing import Lock
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
    strengths_bp_flatte: List[str],
    weaknesses_bp_flatte: List[str],
    human_scores: List[int],
    mode: str,
    config: Config,
    top_k_reviewers: int,
) -> Tuple[Dict[str, Any], Dict[str, List[float]]]:
    intro = paper_data.get('introduction', '')
    profiles = [Profile(**data) for data in author_data.values()]
    profiles_reviewers = [Profile(**data) for data in reviewer_data.values()]
    ref_abstracts = [ref['abstract'] for ref in paper_data.get('references', [])]

    generated_strength, generated_weakness, score, review_per_reviewer = write_review(
        mode,
        intro,
        profiles,
        profiles_reviewers,
        full_content,
        ref_abstracts,
        config,
        top_k_reviewers,
    )

    metrics = compute_review_metrics(
        strengths_bp_flatte,
        weaknesses_bp_flatte,
        generated_strength,
        generated_weakness,
    )
    avg_score = sum(human_scores) / len(human_scores)
    avg_generated_score = sum(score) / len(score)
    dist = abs(avg_score - avg_generated_score)
    results = {
        'paper_id': paper_id,
        'strengths_bp': strengths_bp_flatte,
        'weaknesses_bp': weaknesses_bp_flatte,
        'generated_strength': generated_strength,
        'generated_weakness': generated_weakness,
        'score': human_scores,
        'generated_scores': score,
        'avg_score': avg_score,
        'avg_generated_score': avg_generated_score,
        'score_diff': dist,
        # 'review_per_reviewer': review_per_reviewer,
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
    task: Tuple[
        str,
        Dict[str, Any],
        Dict[str, Any],
        Dict[str, Any],
        Dict[str, Any],
        List[str],
        List[str],
        List[int],
        str,
        Config,
        int,
    ],
) -> Tuple[Dict[str, Sequence[str]], Dict[str, List[float]]]:
    return inference(
        paper_id=task[0],
        paper_data=task[1],
        author_data=task[2],
        reviewer_data=task[3],
        full_content=task[4],
        strengths_bp_flatte=task[5],
        weaknesses_bp_flatte=task[6],
        human_scores=task[7],
        mode=task[8],
        config=task[9],
        top_k_reviewers=task[10],
    )


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
            'reviewer_only',
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
    parser.add_argument(
        '--top_k_reviewers',
        type=int,
        default=5,
        help='Number of top reviewers to consider',
    )
    args = parser.parse_args()

    config = Config(args.config_path)
    top_k_reviewers = args.top_k_reviewers
    dataset = load_papers(args.input_path, args.output_path)
    logger.info(f'Processing {len(dataset)} papers')

    for paper_id, data in tqdm(dataset.items(), desc='Processing papers'):
        full_content = data['full_content']
        paper_data = data['paper_data']
        author_data = data['author_data']
        reviewer_data = data['reviewer_data']
        reference_review = data['reviews']
        human_scores = [
            int(review.get('rating').split(':')[0]) for review in reference_review
        ]
        strengths_bp = [
            review.get('strengths_bullet', '') for review in reference_review
        ]
        # flatten
        strengths_bp_flatten = [item for sublist in strengths_bp for item in sublist]
        weaknesses_bp = [
            review.get('weaknesses_bullet', '') for review in reference_review
        ]
        # flatten
        weaknesses_bp_flatten = [item for sublist in weaknesses_bp for item in sublist]

        results, metrics = inference(
            paper_id,
            paper_data,
            author_data,
            reviewer_data,
            full_content,
            strengths_bp_flatten,
            weaknesses_bp_flatten,
            human_scores,
            args.mode,
            config,
            top_k_reviewers,
        )
        lock = Lock()
        save_results(results, metrics, args.output_path, lock)


if __name__ == '__main__':
    main()
