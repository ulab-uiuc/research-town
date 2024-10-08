
import nltk
from bert_score import score
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer
from typing import Optional
from research_town.utils.model_prompting import model_prompting
# Initialize NLTK resources
nltk.download('punkt')

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
        reference_tokens = nltk.word_tokenize(reference.lower())
        hypothesis_tokens = nltk.word_tokenize(hypothesis.lower())
        smoothie = SmoothingFunction().method4
        bleu_score = sentence_bleu(
            [reference_tokens], hypothesis_tokens, smoothing_function=smoothie
        )
        return float(bleu_score)
    except Exception as e:
        print(f'Error computing BLEU score: {e}')
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
        print(f'Error computing ROUGE-L score: {e}')
        return 0.0


def compute_bertscore(reference: str, hypothesis: str) -> float:
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
        print(f'Error computing BERTScore: {e}')
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
                print('GPT metric response is not a valid float.')
                return None
        else:
            print(
                'Received empty response from model_prompting for GPT metric.'
            )
            return None
    except Exception as e:
        print(f'Error computing GPT-based metric: {e}')
        return None
