from typing import Dict

import nltk
import numpy as np
from bert_score import score
from litellm import embedding
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer

from research_town.utils.model_prompting import model_prompting

# Initialize NLTK resources
nltk.download('punkt')


def compute_bleu(reference: str, hypothesis: str) -> float:
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
    try:
        scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
        scores = scorer.score(reference, hypothesis)
        rouge_l_f1 = scores['rougeL'].fmeasure
        return float(rouge_l_f1)
    except Exception as e:
        print(f'Error computing ROUGE-L score: {e}')
        return 0.0


def compute_bertscore(reference: str, hypothesis: str) -> float:
    try:
        # Compute BERTScore
        P, R, F1 = score(
            [hypothesis], [reference], lang='en', rescale_with_baseline=True
        )
        return float(F1.mean().item())
    except Exception as e:
        print(f'Error computing BERTScore: {e}')
        return 0.0


def compute_gpt_metric(reference: str, generation: str) -> float:
    prompt = [
        {
            'role': 'user',
            'content': (
                'Evaluate the alignment between the following two sets of five core research questions, with a particular emphasis on their objectives, methodologies, and expected outcomes.\n\n'
                'Alignment Criteria Definitions:\n'
                '1. **Objectives**: Do both sets of questions aim to address the same or complementary research goals?\n'
                '2. **Methodologies**: Are the proposed methods similar, compatible, or capable of being effectively integrated?\n'
                '3. **Expected Outcomes**: Are the anticipated research results and impacts consistent or mutually supportive?\n\n'
                'Reference context:\n'
                f'{reference}\n\n'
                'Proposed context:\n'
                f'{generation}\n\n'
                'Based on the above alignment criteria, especially focusing on the methodologies, please provide a similarity score: **1** indicates alignment, and **0** indicates no alignment. **Only output the score without any additional information.**'
            ),
        }
    ]
    response = model_prompting('gpt-4o-mini', prompt)[0]
    score = float(response.strip())
    score = max(0.0, min(1.0, score))
    return score


def compute_embedding_similarity(reference: str, hypothesis: str) -> float:
    try:
        response_ref = embedding(model='text-embedding-3-large', input=[reference])
        response_hyp = embedding(model='text-embedding-3-large', input=[hypothesis])

        embedding_ref = response_ref['data'][0]['embedding']
        embedding_hyp = response_hyp['data'][0]['embedding']

        vec_ref = np.array(embedding_ref)
        vec_hyp = np.array(embedding_hyp)

        cosine_sim = np.dot(vec_ref, vec_hyp) / (
            np.linalg.norm(vec_ref) * np.linalg.norm(vec_hyp)
        )

        return float(cosine_sim)
    except Exception as e:
        print(f'Error computing embedding similarity: {e}')
        return 0.0


def compute_metrics(reference: str, generation: str) -> Dict[str, float]:
    bleu = compute_bleu(reference, generation)
    rouge_l = compute_rouge_l(reference, generation)
    bert_score = compute_bertscore(reference, generation)
    gpt_metric = compute_gpt_metric(reference, generation)
    embedding_similarity = compute_embedding_similarity(reference, generation)

    return {
        'bleu': bleu,
        'rouge_l': rouge_l,
        'gpt_metric_score': gpt_metric,
        'bert_score': bert_score,
        'embedding_similarity': embedding_similarity,
    }
