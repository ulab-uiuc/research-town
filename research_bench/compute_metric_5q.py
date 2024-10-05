import json
import argparse
import logging
from typing import List, Dict, Optional
import sys
import re

# Import necessary libraries for metrics
import nltk
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score
from tqdm import tqdm

# Initialize NLTK resources
nltk.download('punkt')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def parse_5q(text: str):
    """
    Parses the 5Q text into individual questions.

    Args:
        text (str): The 5Q text containing five questions.

    Returns:
        Optional[List[str]]: A list of five question texts if parsing is successful, otherwise None.
    """
    try:
        pattern = r'\[Question (\d+)\](.*?)(?=\[Question \d+\]|\Z)'
        matches = re.findall(pattern, text, re.DOTALL)
        q5_result = {}

        for match in matches:
            question_number = f'q{match[0]}'
            answer = match[1].strip()
            q5_result[question_number] = answer
        return q5_result
    except Exception as e:
        return None

def compute_bleu(reference: str, hypothesis: str) -> float:
    """
    Computes the BLEU score between reference and hypothesis texts.

    Args:
        reference (str): Reference text.
        hypothesis (str): Hypothesis text.

    Returns:
        float: BLEU score.
    """
    try:
        reference_tokens = word_tokenize(reference.lower())
        hypothesis_tokens = word_tokenize(hypothesis.lower())
        smoothie = SmoothingFunction().method4
        bleu_score = sentence_bleu(
            [reference_tokens], hypothesis_tokens, smoothing_function=smoothie
        )
        return float(bleu_score)
    except Exception as e:
        logger.error(f'Error computing BLEU score: {e}')
        return 0.0

def compute_rouge_l(reference: str, hypothesis: str) -> float:
    """
    Computes the ROUGE-L score between reference and hypothesis texts.

    Args:
        reference (str): Reference text.
        hypothesis (str): Hypothesis text.

    Returns:
        float: ROUGE-L F1 score.
    """
    try:
        scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
        scores = scorer.score(reference, hypothesis)
        rouge_l_f1 = scores['rougeL'].fmeasure
        return float(rouge_l_f1)
    except Exception as e:
        logger.error(f'Error computing ROUGE-L score: {e}')
        return 0.0

def compute_bertscore_metric(reference: str, hypothesis: str) -> float:
    """
    Computes the BERTScore between reference and hypothesis texts.

    Args:
        reference (str): Reference text.
        hypothesis (str): Hypothesis text.

    Returns:
        float: BERTScore F1 score.
    """
    try:
        # Compute BERTScore
        P, R, F1 = score(
            [hypothesis], [reference], lang='en', rescale_with_baseline=True
        )
        return float(F1.mean().item())
    except Exception as e:
        logger.error(f'Error computing BERTScore: {e}')
        return 0.0

def process_jsonl(input_path: str, output_path: str):
    """
    Processes the input JSONL file, computes metrics for each question in each entry,
    and writes the results to a new JSONL file.
    Also computes and logs the average of each metric.

    Args:
        input_path (str): Path to the input JSONL file.
        output_path (str): Path to the output JSONL file.
    """
    # Initialize lists to store metric values for averaging
    bleu_scores = []
    rouge_l_scores = []
    bert_scores = []

    total_entries = 0
    total_questions = 0

    try:
        # First, count total lines for tqdm progress bar
        with open(input_path, 'r', encoding='utf-8') as infile:
            total_lines = sum(1 for _ in infile)

        with open(input_path, 'r', encoding='utf-8') as infile:
            for line in tqdm(infile, total=total_lines, desc="Processing JSONL"):
                total_entries += 1
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f'Error decoding JSON on line {total_entries}: {e}')
                    continue

                # Extract required fields
                paper_key = data.get('paper_key', '')
                current_5q = data.get('current_5q', '')
                proposal_5q = data.get('proposal_5q', '')

                if not paper_key or not current_5q or not proposal_5q:
                    logger.warning(f'Missing fields in entry {total_entries}. Skipping.')
                    continue

                # Parse the 5Q texts into individual questions
                current_questions = parse_5q(current_5q)
                print(current_questions)
                proposal_questions = parse_5q(proposal_5q)
                print(proposal_questions)
                if not current_questions or not proposal_questions:
                    logger.warning(f'Failed to parse 5Q in entry {total_entries}. Skipping.')
                    continue

                metrics = {}
                for i in range(5):
                    q_num = i + 1
                    current_q = current_questions[f'q{i+1}']
                    proposal_q = proposal_questions[f'q{i+1}']
                    print(current_q)
                    print(proposal_q)
                    bleu = compute_bleu(current_q, proposal_q)
                    rouge_l = compute_rouge_l(current_q, proposal_q)
                    bertscore = compute_bertscore_metric(current_q, proposal_q)

                    metrics[f'Question {q_num}'] = {
                        'bleu': bleu,
                        'rouge_l': rouge_l,
                        'bertscore': bertscore
                    }

                    # Append metrics to lists for averaging
                    bleu_scores.append(bleu)
                    rouge_l_scores.append(rouge_l)
                    bert_scores.append(bertscore)
                    total_questions += 1

                # Prepare the output data
                output_data = {
                    'paper_key': paper_key,
                    'current_5q': current_5q,
                    'proposal_5q': proposal_5q,
                    'metrics': metrics
                }

                # Write the output data as a JSON line
                with open(output_path, 'a', encoding='utf-8') as outfile:
                    outfile.write(json.dumps(output_data, ensure_ascii=False) + '\n')
                    outfile.flush()

                logger.info(f'Processed entry {total_entries}: paper_key={paper_key}')

        # Compute average metrics
        avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
        avg_rouge_l = sum(rouge_l_scores) / len(rouge_l_scores) if rouge_l_scores else 0.0
        avg_bertscore = sum(bert_scores) / len(bert_scores) if bert_scores else 0.0

        # Log the average metrics
        logger.info('--- Average Metrics ---')
        logger.info(f'Average BLEU Score: {avg_bleu:.4f}')
        logger.info(f'Average ROUGE-L Score: {avg_rouge_l:.4f}')
        logger.info(f'Average BERTScore: {avg_bertscore:.4f}')

    except FileNotFoundError as e:
        logger.error(f'File not found: {e}')
    except Exception as e:
        logger.error(f'An error occurred during processing: {e}')

def main():
    """
    The main function parses command-line arguments and initiates the JSONL processing.
    """
    parser = argparse.ArgumentParser(description='Process a JSONL file to compute text similarity metrics for each question.')
    parser.add_argument('input_path', type=str, help='Path to the input JSONL file.')
    parser.add_argument('output_path', type=str, help='Path to the output JSONL file.')

    args = parser.parse_args()
    print(args)
    process_jsonl(args.input_path, args.output_path)

if __name__ == '__main__':
    main()