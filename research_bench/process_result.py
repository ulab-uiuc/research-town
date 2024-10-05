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

def compute_average_metrics(file_path: str) -> Dict[str, float]:
    """
    Computes the average of BLEU, ROUGE-L, BERTScore, and GPT-based scores for a given JSONL file.

    Args:
        file_path (str): Path to the JSONL file.

    Returns:
        Dict[str, float]: A dictionary with average values of the four metrics.
    """
    bleu_total = 0.0
    rouge_l_total = 0.0
    bertscore_total = 0.0
    gpt_score_total = 0.0
    count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    
                    # Extract metrics
                    bleu = data.get('bleu')
                    rouge_l = data.get('rouge_l')
                    bertscore = data.get('bertscore')
                    gpt_score = data.get('gpt_score')

                    # Validate that all metrics are present and are numbers
                    if not all(isinstance(metric, (int, float)) for metric in [bleu, rouge_l, bertscore, gpt_score]):
                        logger.warning(f'Non-numeric or missing metrics in file "{file_path}" at line {line_number}. Skipping entry.')
                        continue

                    bleu_total += bleu
                    rouge_l_total += rouge_l
                    bertscore_total += bertscore
                    gpt_score_total += gpt_score
                    count += 1

                except json.JSONDecodeError as e:
                    logger.error(f'JSON decode error in file "{file_path}" at line {line_number}: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error in file "{file_path}" at line {line_number}: {e}')

        if count == 0:
            logger.warning(f'No valid entries found in file "{file_path}".')
            return {
                'bleu': 0.0,
                'rouge_l': 0.0,
                'bertscore': 0.0,
                'gpt_score': 0.0
            }

        # Calculate averages
        average_metrics = {
            'bleu': bleu_total / count,
            'rouge_l': rouge_l_total / count,
            'bertscore': bertscore_total / count,
            'gpt_score': gpt_score_total / count
        }

        return average_metrics

    except FileNotFoundError:
        logger.error(f'File not found: {file_path}')
        return {
            'bleu': 0.0,
            'rouge_l': 0.0,
            'bertscore': 0.0,
            'gpt_score': 0.0
        }
    except Exception as e:
        logger.error(f'Error processing file "{file_path}": {e}')
        return {
            'bleu': 0.0,
            'rouge_l': 0.0,
            'bertscore': 0.0,
            'gpt_score': 0.0
        }

def process_directory(input_dir: str) -> List[Dict[str, str]]:
    """
    Processes all JSONL files in the given directory and computes average metrics for each file.

    Args:
        input_dir (str): Path to the directory containing JSONL files.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing filenames and their corresponding average metrics.
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
            results.append({
                'filename': filename,
                'average_bleu': f"{averages['bleu']:.6f}",
                'average_rouge_l': f"{averages['rouge_l']:.6f}",
                'average_bertscore': f"{averages['bertscore']:.6f}",
                'average_gpt_score': f"{averages['gpt_score']:.6f}"
            })

    return results

def save_results(results: List[Dict[str, str]], output_file: str):
    """
    Saves the computed average metrics to a specified output file.

    Args:
        results (List[Dict[str, str]]): List of results containing filenames and average metrics.
        output_file (str): Path to the output file.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write('filename,average_bleu,average_rouge_l,average_bertscore,average_gpt_score\n')
            # Write each result
            for result in results:
                line = f"{result['filename']},{result['average_bleu']},{result['average_rouge_l']},{result['average_bertscore']},{result['average_gpt_score']}\n"
                f.write(line)
        logger.info(f'Results saved to "{output_file}".')
    except Exception as e:
        logger.error(f'Error saving results to "{output_file}": {e}')

def main():
    """
    The main function parses command-line arguments and initiates the processing of JSONL files.
    """
    input_dir = './results_combine/'
    output_file = './results_combine/main_compute/average_metrics.csv'
    
    # Process the directory and compute averages
    results = process_directory(input_dir)

    if not results:
        logger.warning('No results to save.')
        return

    # Save the results to the output file
    save_results(results, output_file)

    # Also, print the results to the console
    print(f'{"Filename":<30} {"BLEU":<10} {"ROUGE-L":<10} {"BERTScore":<12} {"GPT Score":<10}')
    print('-' * 72)
    for result in results:
        print(f"{result['filename']:<30} {result['average_bleu']:<10} {result['average_rouge_l']:<10} {result['average_bertscore']:<12} {result['average_gpt_score']:<10}")

if __name__ == '__main__':
    main()