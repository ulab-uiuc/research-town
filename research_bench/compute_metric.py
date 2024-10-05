import json
import argparse
import logging
from typing import Optional, List
import sys

# Import necessary libraries for metrics
import nltk
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score
from research_town.utils.model_prompting import model_prompting
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

def compute_gpt_metric(current_5q: str, proposal_5q: str) -> Optional[float]:
    """
    Computes a custom GPT-based metric to evaluate if the proposal_5q reflects the current_5q.

    Args:
        current_5q (str): The current five core questions.
        proposal_5q (str): The proposed five core questions.

    Returns:
        Optional[float]: A similarity score between 0 and 1.
    """
    try:
        prompt = [
            {
                'role': 'user',
                'content': (
                    'Evaluate the alignment between the following two sets of five core research questions, with a particular emphasis on their objectives, methodologies, and expected outcomes.\n\n'
                    'Alignment Criteria Definitions:\n'
                    '1. **Objectives**: Do both sets of questions aim to address the same or complementary research goals?\n'
                    '2. **Methodologies**: Are the proposed methods similar, compatible, or capable of being effectively integrated?\n'
                    '3. **Expected Outcomes**: Are the anticipated research results and impacts consistent or mutually supportive?\n\n'
                    'Current Five Research Questions (Current 5Q):\n'
                    f'{current_5q}\n\n'
                    'Proposed Five Research Questions (Proposal 5Q):\n'
                    f'{proposal_5q}\n\n'
                    'Based on the above alignment criteria, especially focusing on the methodologies, please provide a similarity score: **1** indicates alignment, and **0** indicates no alignment. **Only output the score without any additional information.**'
                ),
            }
        ]
        response = model_prompting('gpt-4o-mini', prompt, mode='TEST')

        if response and len(response) > 0 and len(response[0]) > 0:
            try:
                score = float(response[0].strip())
                # Ensure the score is between 0 and 1
                score = max(0.0, min(1.0, score))
                return score
            except ValueError:
                logger.warning('GPT metric response is not a valid float.')
                return None
        else:
            logger.warning(
                'Received empty response from model_prompting for GPT metric.'
            )
            return None
    except Exception as e:
        logger.error(f'Error computing GPT-based metric: {e}')
        return None

def process_jsonl(input_path: str, output_path: str):
    """
    Processes the input JSONL file, computes metrics for each entry, and writes the results to a new JSONL file.
    Also computes and logs the average of each metric.

    Args:
        input_path (str): Path to the input JSONL file.
        output_path (str): Path to the output JSONL file.
    """
    # Initialize lists to store metric values for averaging
    bleu_scores = []
    rouge_l_scores = []
    bert_scores = []
    gpt_scores = []

    total_entries = 0

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            for line in infile:
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

                # Compute metrics
                bleu = compute_bleu(current_5q, proposal_5q)
                rouge_l = compute_rouge_l(current_5q, proposal_5q)
                bertscore = compute_bertscore_metric(current_5q, proposal_5q)
                gpt_score = compute_gpt_metric(current_5q, proposal_5q)

                # Append metrics to lists for averaging
                bleu_scores.append(bleu)
                rouge_l_scores.append(rouge_l)
                bert_scores.append(bertscore)
                if gpt_score is not None:
                    gpt_scores.append(gpt_score)

                # Prepare the output data
                output_data = {
                    'paper_key': paper_key,
                    'current_5q': current_5q,
                    'proposal_5q': proposal_5q,
                    'bleu': bleu,
                    'rouge_l': rouge_l,
                    'bertscore': bertscore,
                    'gpt_score': gpt_score
                }

                # Write the output data as a JSON line
                with open(output_path, 'a', encoding='utf-8') as outfile:
                    outfile.write(json.dumps(output_data, ensure_ascii=False) + '\n')

                logger.info(f'Processed entry {total_entries}: paper_key={paper_key}')

        # Compute average metrics
        avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
        avg_rouge_l = sum(rouge_l_scores) / len(rouge_l_scores) if rouge_l_scores else 0.0
        avg_bertscore = sum(bert_scores) / len(bert_scores) if bert_scores else 0.0
        avg_gpt_score = sum(gpt_scores) / len(gpt_scores) if gpt_scores else 0.0

        # Log the average metrics
        logger.info('--- Average Metrics ---')
        logger.info(f'Average BLEU Score: {avg_bleu:.4f}')
        logger.info(f'Average ROUGE-L Score: {avg_rouge_l:.4f}')
        logger.info(f'Average BERTScore: {avg_bertscore:.4f}')
        logger.info(f'Average GPT-based Score: {avg_gpt_score:.4f}')

    except FileNotFoundError as e:
        logger.error(f'File not found: {e}')
    except Exception as e:
        logger.error(f'An error occurred during processing: {e}')

def main():
    """
    The main function parses command-line arguments and initiates the JSONL processing.
    """
    parser = argparse.ArgumentParser(description='Process a JSONL file to compute text similarity metrics.')
    parser.add_argument('input_path', type=str, help='Path to the input JSONL file.')
    parser.add_argument('output_path', type=str, help='Path to the output JSONL file.')

    args = parser.parse_args()

    process_jsonl(args.input_path, args.output_path)

if __name__ == '__main__':
    main()