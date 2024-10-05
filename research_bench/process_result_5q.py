import os
import json
import argparse
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def compute_average_metrics(file_path: str) -> Dict[str, Dict[str, float]]:
    """
    Computes the average of BLEU, ROUGE-L, and BERTScore for each question in a given JSONL file.

    Args:
        file_path (str): Path to the JSONL file.

    Returns:
        Dict[str, Dict[str, float]]: A dictionary where each key is a question and the value is another
                                     dictionary with average 'bleu', 'rouge_l', and 'bertscore'.
    """
    metrics_totals = {}
    metrics_counts = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    
                    # Extract metrics
                    metrics = data.get('metrics')
                    if not isinstance(metrics, dict):
                        logger.warning(f'No "metrics" dictionary found in file "{file_path}" at line {line_number}. Skipping entry.')
                        continue
                    
                    for question, q_metrics in metrics.items():
                        if not isinstance(q_metrics, dict):
                            logger.warning(f'Invalid metrics format for "{question}" in file "{file_path}" at line {line_number}. Skipping this question.')
                            continue
                        
                        bleu = q_metrics.get('bleu')
                        rouge_l = q_metrics.get('rouge_l')
                        bertscore = q_metrics.get('bertscore')
                        
                        # Validate that all metrics are present and are numbers
                        if not all(isinstance(metric, (int, float)) for metric in [bleu, rouge_l, bertscore]):
                            logger.warning(f'Non-numeric or missing metrics for "{question}" in file "{file_path}" at line {line_number}. Skipping this question.')
                            continue
                        
                        if question not in metrics_totals:
                            metrics_totals[question] = {'bleu': 0.0, 'rouge_l': 0.0, 'bertscore': 0.0}
                            metrics_counts[question] = 0
                        
                        metrics_totals[question]['bleu'] += bleu
                        metrics_totals[question]['rouge_l'] += rouge_l
                        metrics_totals[question]['bertscore'] += bertscore
                        metrics_counts[question] += 1

                except json.JSONDecodeError as e:
                    logger.error(f'JSON decode error in file "{file_path}" at line {line_number}: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error in file "{file_path}" at line {line_number}: {e}')

        if not metrics_totals:
            logger.warning(f'No valid metrics found in file "{file_path}".')
            return {}

        # Calculate averages
        average_metrics = {}
        for question, totals in metrics_totals.items():
            count = metrics_counts.get(question, 0)
            if count == 0:
                logger.warning(f'No valid entries for "{question}" in file "{file_path}". Skipping averages.')
                continue
            average_metrics[question] = {
                'bleu': totals['bleu'] / count,
                'rouge_l': totals['rouge_l'] / count,
                'bertscore': totals['bertscore'] / count
            }

        return average_metrics

    except FileNotFoundError:
        logger.error(f'File not found: {file_path}')
        return {}
    except Exception as e:
        logger.error(f'Error processing file "{file_path}": {e}')
        return {}

def process_directory(input_dir: str) -> List[Dict[str, str]]:
    """
    Processes all JSONL files in the given directory and computes average metrics for each question in each file.

    Args:
        input_dir (str): Path to the directory containing JSONL files.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing filenames, questions, and their corresponding average metrics.
    """
    results = []

    if not os.path.isdir(input_dir):
        logger.error(f'The provided path is not a directory or does not exist: {input_dir}')
        return results

    # Iterate over all files in the directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.jsonl'):
            file_path = os.path.join(input_dir, filename)
            logger.info(f'Processing file: {filename}')
            averages = compute_average_metrics(file_path)
            
            if not averages:
                logger.warning(f'No averages computed for file "{filename}". Skipping.')
                continue

            for question, metrics in averages.items():
                results.append({
                    'filename': filename,
                    'question': question,
                    'average_bleu': f"{metrics['bleu']:.6f}",
                    'average_rouge_l': f"{metrics['rouge_l']:.6f}",
                    'average_bertscore': f"{metrics['bertscore']:.6f}"
                })

    return results

def save_results(results: List[Dict[str, str]], output_file: str):
    """
    Saves the computed average metrics to a specified output file.

    Args:
        results (List[Dict[str, str]]): List of results containing filenames, questions, and average metrics.
        output_file (str): Path to the output CSV file.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write('filename,question,average_bleu,average_rouge_l,average_bertscore\n')
            # Write each result
            for result in results:
                line = f"{result['filename']},{result['question']},{result['average_bleu']},{result['average_rouge_l']},{result['average_bertscore']}\n"
                f.write(line)
        logger.info(f'Results saved to "{output_file}".')
    except Exception as e:
        logger.error(f'Error saving results to "{output_file}": {e}')

def main():
    """
    The main function parses command-line arguments and initiates the processing of JSONL files.
    """

    input_dir = "./results_combine/main_compute_5q"
    output_file = "./results_combine/main_compute_5q/average_metrics.csv"

    # Process the directory and compute averages
    results = process_directory(input_dir)

    if not results:
        logger.warning('No results to save.')
        return

    # Save the results to the output file
    save_results(results, output_file)

    # Also, print the results to the console
    print(f'{"Filename":<30} {"Question":<15} {"BLEU":<10} {"ROUGE-L":<10} {"BERTScore":<12}')
    print('-' * 80)
    for result in results:
        print(f"{result['filename']:<30} {result['question']:<15} {result['average_bleu']:<10} {result['average_rouge_l']:<10} {result['average_bertscore']:<12}")

if __name__ == '__main__':
    main()