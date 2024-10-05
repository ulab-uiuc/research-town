import os
import json
import argparse
import logging
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def load_gpt_scores(file_path: str) -> Dict[str, float]:
    """
    Loads the gpt_score from a JSONL file, indexed by paper_key.

    Args:
        file_path (str): Path to the JSONL file.

    Returns:
        Dict[str, float]: A dictionary mapping paper_key to gpt_score.
    """
    gpt_scores = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    paper_key = data.get('paper_key')
                    gpt_score = data.get('gpt_metric_score')

                    if paper_key is None:
                        logger.warning(f'Missing "paper_key" in file "{file_path}" at line {line_number}. Skipping entry.')
                        continue

                    if not isinstance(gpt_score, (int, float)):
                        logger.warning(f'Invalid or missing "gpt_score" for paper_key "{paper_key}" in file "{file_path}" at line {line_number}. Skipping entry.')
                        continue

                    if paper_key in gpt_scores:
                        logger.warning(f'Duplicate "paper_key" "{paper_key}" found in file "{file_path}" at line {line_number}. Overwriting previous gpt_score.')
                    
                    gpt_scores[paper_key] = gpt_score

                except json.JSONDecodeError as e:
                    logger.error(f'JSON decode error in file "{file_path}" at line {line_number}: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error in file "{file_path}" at line {line_number}: {e}')
    except FileNotFoundError:
        logger.error(f'File not found: {file_path}')
    except Exception as e:
        logger.error(f'Error reading file "{file_path}": {e}')
    
    logger.info(f'Loaded {len(gpt_scores)} entries from "{file_path}".')
    return gpt_scores

def compare_gpt_scores(scores1: Dict[str, float], scores2: Dict[str, float]) -> Tuple[int, int, int, int]:
    """
    Compares gpt_scores between two dictionaries based on paper_key.

    Args:
        scores1 (Dict[str, float]): GPT scores from the first file.
        scores2 (Dict[str, float]): GPT scores from the second file.

    Returns:
        Tuple[int, int, int, int]: Number of comparisons, wins, ties, and losses.
    """
    wins = 0
    ties = 0
    losses = 0
    total = 0

    # Find common paper_keys
    common_keys = set(scores1.keys()).intersection(set(scores2.keys()))
    logger.info(f'Found {len(common_keys)} common paper_keys to compare.')

    for key in common_keys:
        score1 = scores1[key]
        score2 = scores2[key]

        if score1 > score2:
            wins += 1
        elif score1 == score2:
            ties += 1
        else:
            losses += 1
        total += 1

    # Log unmatched keys
    only_in_1 = set(scores1.keys()) - set(scores2.keys())
    only_in_2 = set(scores2.keys()) - set(scores1.keys())

    if only_in_1:
        logger.warning(f'{len(only_in_1)} paper_keys are only in the first file and will be ignored.')
    if only_in_2:
        logger.warning(f'{len(only_in_2)} paper_keys are only in the second file and will be ignored.')

    return total, wins, ties, losses

def calculate_rates(total: int, wins: int, ties: int, losses: int) -> Tuple[float, float, float]:
    """
    Calculates win rate, tie rate, and lose rate.

    Args:
        total (int): Total number of comparisons.
        wins (int): Number of wins.
        ties (int): Number of ties.
        losses (int): Number of losses.

    Returns:
        Tuple[float, float, float]: Win rate, tie rate, lose rate as percentages.
    """
    if total == 0:
        return 0.0, 0.0, 0.0

    win_rate = (wins / total) * 100
    tie_rate = (ties / total) * 100
    lose_rate = (losses / total) * 100

    return win_rate, tie_rate, lose_rate

def save_results(output_file: str, total: int, wins: int, ties: int, losses: int, win_rate: float, tie_rate: float, lose_rate: float):
    """
    Saves the comparison results to a CSV file.

    Args:
        output_file (str): Path to the output CSV file.
        total (int): Total comparisons.
        wins (int): Number of wins.
        ties (int): Number of ties.
        losses (int): Number of losses.
        win_rate (float): Win rate percentage.
        tie_rate (float): Tie rate percentage.
        lose_rate (float): Lose rate percentage.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('Total Comparisons,Wins,Ties,Losses,Win Rate (%),Tie Rate (%),Lose Rate (%)\n')
            f.write(f'{total},{wins},{ties},{losses},{win_rate:.2f},{tie_rate:.2f},{lose_rate:.2f}\n')
        logger.info(f'Results saved to "{output_file}".')
    except Exception as e:
        logger.error(f'Error saving results to "{output_file}": {e}')

def main():
    """
    The main function parses command-line arguments and initiates the comparison of GPT scores.
    """
    file1 = './results_combine/interdisplinary_compute/research_bench_result_4o_mini_interdisplinary.jsonl' #args.file1
    file2 = './results_combine/interdisplinary_compute/research_bench_result_4o_mini_interdisplinary_single_agent.jsonl' #args.file2
    output_file = './results_combine/main_compute/gpt_score_llama3_comparison.csv' #args.output

    logger.info(f'Loading GPT scores from "{file1}".')
    scores1 = load_gpt_scores(file1)

    logger.info(f'Loading GPT scores from "{file2}".')
    scores2 = load_gpt_scores(file2)

    logger.info('Comparing GPT scores.')
    total, wins, ties, losses = compare_gpt_scores(scores1, scores2)

    win_rate, tie_rate, lose_rate = calculate_rates(total, wins, ties, losses)

    # Print results
    print('\nGPT Score Comparison Results:')
    print('----------------------------------------')
    print(f'Total Comparisons : {total}')
    print(f'Wins (File1 > File2) : {wins} ({win_rate:.2f}%)')
    print(f'Ties (File1 = File2) : {ties} ({tie_rate:.2f}%)')
    print(f'Losses (File1 < File2) : {losses} ({lose_rate:.2f}%)')
    print('----------------------------------------\n')

    # Save results to CSV
    save_results(output_file, total, wins, ties, losses, win_rate, tie_rate, lose_rate)

if __name__ == '__main__':
    main()