import re
from typing import Any, Dict, List

import nltk
import numpy as np
from bert_score import score
from litellm import embedding
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer
from voyageai.client import Client

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


def compute_proposal_gpt_metric(reference: str, generation: str) -> float:
    prompt = [
        {
            'role': 'user',
            'content': (
                'Evaluate the alignment between the following two sets of paragraphs, with a particular emphasis on their objectives, methodologies, and expected outcomes.\n\n'
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
    response = model_prompting('gpt-4o-mini', prompt, temperature=0.0)[0]
    score = float(response.strip())
    score = max(0.0, min(1.0, score))
    return score


def compute_review_gpt_metric(reference: str, generation: str) -> float:
    return 0


def compute_openai_embedding_similarity(reference: str, hypothesis: str) -> float:
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


def compute_voyageai_embedding_similarity(reference: str, hypothesis: str) -> float:
    vo = Client()
    try:
        response_ref = vo.embed(
            model='voyage-3', texts=[reference], input_type='document'
        )
        response_hyp = vo.embed(
            model='voyage-3', texts=[hypothesis], input_type='document'
        )

        embedding_ref = response_ref.embeddings[0]
        embedding_hyp = response_hyp.embeddings[0]

        vec_ref = np.array(embedding_ref)
        vec_hyp = np.array(embedding_hyp)

        cosine_sim = np.dot(vec_ref, vec_hyp) / (
            np.linalg.norm(vec_ref) * np.linalg.norm(vec_hyp)
        )

        return float(cosine_sim)
    except Exception as e:
        print(f'Error computing embedding similarity: {e}')
        return 0.0


def extract_and_clean_question_content(
    text: str, question_prompts: List[str]
) -> List[str]:
    question_contents = []
    for i, prompt in enumerate(question_prompts):
        start = text.find(prompt)
        end = (
            text.find(question_prompts[i + 1])
            if i + 1 < len(question_prompts)
            else len(text)
        )

        if start != -1:
            content = text[start + len(prompt) : end].strip()
            content = re.sub(r'[\*\#]+', '', content).strip()
            content = content.split('\n', 1)[0].strip()
            question_contents.append(content)
        else:
            question_contents.append('')
    return question_contents


def compute_openai_embedding_similarity_per_question(
    reference: str, hypothesis: str
) -> List[float]:
    try:
        questions = [
            'What is the problem?',
            'Why is it interesting and important?',
            'Why is it hard?',
            "Why hasn't it been solved before?",
            'What are the key components of my approach and results?',
        ]

        ref_questions = extract_and_clean_question_content(reference, questions)
        hyp_questions = extract_and_clean_question_content(hypothesis, questions)

        similarities = []

        for ref_text, hyp_text in zip(ref_questions, hyp_questions):
            if not ref_text or not hyp_text:
                print(f'Empty question: {ref_text} vs {hyp_text}')
                similarities.append(0.0)
                continue

            cosine_sim = compute_openai_embedding_similarity(ref_text, hyp_text)
            similarities.append(float(cosine_sim))

        return similarities

    except Exception as e:
        print(f'Error computing embedding similarity per question: {e}')
        return [0.0] * len(questions)


def compute_openai_embedding_similarity_per_section(
    reference: str, hypothesis: str
) -> List[float]:
    try:
        sections = [
            'Strength -',
            'Weakness -',
        ]

        ref_sections = extract_and_clean_question_content(reference, sections)
        hyp_sections = extract_and_clean_question_content(hypothesis, sections)

        similarities = []

        for ref_text, hyp_text in zip(ref_sections, hyp_sections):
            if not ref_text or not hyp_text:
                print(f'Empty section: {ref_text} vs {hyp_text}')
                similarities.append(0.0)
                continue

            cosine_sim = compute_openai_embedding_similarity(ref_text, hyp_text)
            similarities.append(float(cosine_sim))

        return similarities

    except Exception as e:
        print(f'Error computing embedding similarity per section: {e}')
        return [0.0] * len(sections)


def compute_voyageai_embedding_similarity_per_question(
    reference: str, hypothesis: str
) -> List[float]:
    try:
        questions = [
            'What is the problem?',
            'Why is it interesting and important?',
            'Why is it hard?',
            "Why hasn't it been solved before?",
            'What are the key components of my approach and results?',
        ]

        ref_questions = extract_and_clean_question_content(reference, questions)
        hyp_questions = extract_and_clean_question_content(hypothesis, questions)

        similarities = []

        for ref_text, hyp_text in zip(ref_questions, hyp_questions):
            if not ref_text or not hyp_text:
                print(f'Empty question: {ref_text} vs {hyp_text}')
                similarities.append(0.0)
                continue

            cosine_sim = compute_voyageai_embedding_similarity(ref_text, hyp_text)
            similarities.append(float(cosine_sim))

        return similarities

    except Exception as e:
        print(f'Error computing embedding similarity per question: {e}')
        return [0.0] * len(questions)


def compute_voyageai_embedding_similarity_per_section(
    reference: str, hypothesis: str
) -> List[float]:
    try:
        sections = [
            'Strength -',
            'Weakness -',
        ]

        ref_sections = extract_and_clean_question_content(reference, sections)
        hyp_sections = extract_and_clean_question_content(hypothesis, sections)

        similarities = []

        for ref_text, hyp_text in zip(ref_sections, hyp_sections):
            if not ref_text or not hyp_text:
                print(f'Empty section: {ref_text} vs {hyp_text}')
                similarities.append(0.0)
                continue

            cosine_sim = compute_voyageai_embedding_similarity(ref_text, hyp_text)
            similarities.append(float(cosine_sim))

        return similarities

    except Exception as e:
        print(f'Error computing embedding similarity per section: {e}')
        return [0.0] * len(sections)


def compute_proposal_metrics(reference: str, generation: str) -> Dict[str, float]:
    bleu = compute_bleu(reference, generation)
    rouge_l = compute_rouge_l(reference, generation)
    bert_score = compute_bertscore(reference, generation)
    gpt_metric = compute_proposal_gpt_metric(reference, generation)
    openai_sim = compute_openai_embedding_similarity(reference, generation)
    voyageai_sim = compute_voyageai_embedding_similarity(reference, generation)
    openai_sim_per_question = compute_openai_embedding_similarity_per_question(
        reference, generation
    )
    voyageai_sim_per_question = compute_voyageai_embedding_similarity_per_question(
        reference, generation
    )

    return {
        'bleu': bleu,
        'rouge_l': rouge_l,
        'gpt_metric_score': gpt_metric,
        'bert_score': bert_score,
        'openai_sim': openai_sim,
        'voyageai_sim': voyageai_sim,
        'openai_sim_q1': openai_sim_per_question[0],
        'openai_sim_q2': openai_sim_per_question[1],
        'openai_sim_q3': openai_sim_per_question[2],
        'openai_sim_q4': openai_sim_per_question[3],
        'openai_sim_q5': openai_sim_per_question[4],
        'voyageai_sim_q1': voyageai_sim_per_question[0],
        'voyageai_sim_q2': voyageai_sim_per_question[1],
        'voyageai_sim_q3': voyageai_sim_per_question[2],
        'voyageai_sim_q4': voyageai_sim_per_question[3],
        'voyageai_sim_q5': voyageai_sim_per_question[4],
    }


def compute_review_metrics(
    strengths: List[str],
    weaknesses: List[str],
    generated_strength: str,
    generated_weakness: str,
) -> Dict[str, List[float]]:
    metrics_raw: Dict[str, Any] = {
        # 'bleu': [],
        # 'rouge_l': [],
        # 'bert_score': [],
        # 'openai_sim': [],
        # 'voyageai_sim': [],
        # 'openai_sim_strength': [],
        # 'openai_sim_weakness': [],
        # 'voyageai_sim_strength': [],
        # 'voyageai_sim_weakness': [],
        'openai_strength': 0.0,
        'openai_weakness': 0.0,
        'voyageai_strength': 0.0,
        'voyageai_weakness': 0.0,
        'openai_sim_strengths': [],
        'openai_sim_weaknesses': [],
        'voyageai_sim_strengths': [],
        'voyageai_sim_weaknesses': [],
        'generated_strength_matchings_openai': [],
        'generated_weakness_matchings_openai': [],
        'generated_strength_matchings_voyageai': [],
        'generated_weakness_matchings_voyageai': [],
    }
    # for each generated strength and weakness
    # find most similar strength or weakness
    # put it in openai_sim_strengths or openai_sim_weaknesses, or voyageai_sim_strengths or voyageai_sim_weaknesses
    # then compute the average similarity

    openai_sim_strengths = []
    openai_sim_weaknesses = []
    voyageai_sim_strengths = []
    voyageai_sim_weaknesses = []

    all_strength_openai_embeddings = []
    all_weakness_openai_embeddings = []
    all_strength_voyageai_embeddings = []
    all_weakness_voyageai_embeddings = []
    generated_strength_matchings_openai = []
    generated_weakness_matchings_openai = []
    generated_strength_matchings_voyageai = []
    generated_weakness_matchings_voyageai = []
    vo = Client()

    # as a precaution, remove all ''s and Nones from strengths and weaknesses
    strengths = [strength for strength in strengths if strength]
    weaknesses = [weakness for weakness in weaknesses if weakness]

    for strength in strengths:
        response = embedding(model='text-embedding-3-large', input=[strength])
        embedding_strength = response['data'][0]['embedding']
        all_strength_openai_embeddings.append(embedding_strength)

        response = vo.embed(model='voyage-3', texts=[strength], input_type='document')
        embedding_strength = response.embeddings[0]
        all_strength_voyageai_embeddings.append(embedding_strength)

    for weakness in weaknesses:
        response = embedding(model='text-embedding-3-large', input=[weakness])
        embedding_weakness = response['data'][0]['embedding']
        all_weakness_openai_embeddings.append(embedding_weakness)

        response = vo.embed(model='voyage-3', texts=[weakness], input_type='document')
        embedding_weakness = response.embeddings[0]
        all_weakness_voyageai_embeddings.append(embedding_weakness)

    for generated_strength in generated_strength.split('\n'):
        if generated_strength:
            response = embedding(
                model='text-embedding-3-large', input=[generated_strength]
            )
            embedding_strength = response['data'][0]['embedding']
            max_sim = -1.0
            max_idx = -1
            for i, strength in enumerate(all_strength_openai_embeddings):
                cosine_sim = np.dot(embedding_strength, strength) / (
                    np.linalg.norm(embedding_strength) * np.linalg.norm(strength)
                )
                if cosine_sim > max_sim:
                    max_sim = cosine_sim
                    max_idx = i
            openai_sim_strengths.append(max_sim)
            generated_strength_matchings_openai.append(
                {
                    'generated': generated_strength,
                    'matched': strengths[max_idx],
                    'similarity': max_sim,
                }
            )

            response = vo.embed(
                model='voyage-3', texts=[generated_strength], input_type='document'
            )
            embedding_strength = response.embeddings[0]
            max_sim = -1.0
            max_idx = -1
            for i, strength in enumerate(all_strength_voyageai_embeddings):
                cosine_sim = np.dot(embedding_strength, strength) / (
                    np.linalg.norm(embedding_strength) * np.linalg.norm(strength)
                )
                if cosine_sim > max_sim:
                    max_sim = cosine_sim
                    max_idx = i
            voyageai_sim_strengths.append(max_sim)
            generated_strength_matchings_voyageai.append(
                {
                    'generated': generated_strength,
                    'matched': strengths[max_idx],
                    'similarity': max_sim,
                }
            )

    for generated_weakness in generated_weakness.split('\n'):
        if generated_weakness:
            response = embedding(
                model='text-embedding-3-large', input=[generated_weakness]
            )
            embedding_weakness = response['data'][0]['embedding']
            max_sim = -1.0
            max_idx = -1
            for i, weakness in enumerate(all_weakness_openai_embeddings):
                cosine_sim = np.dot(embedding_weakness, weakness) / (
                    np.linalg.norm(embedding_weakness) * np.linalg.norm(weakness)
                )
                if cosine_sim > max_sim:
                    max_sim = cosine_sim
                    max_idx = i
            openai_sim_weaknesses.append(max_sim)
            generated_weakness_matchings_openai.append(
                {
                    'generated': generated_weakness,
                    'matched': weaknesses[max_idx],
                    'similarity': max_sim,
                }
            )

            response = vo.embed(
                model='voyage-3', texts=[generated_weakness], input_type='document'
            )
            embedding_weakness = response.embeddings[0]
            max_sim = -1.0
            max_idx = -1
            for i, weakness in enumerate(all_weakness_voyageai_embeddings):
                cosine_sim = np.dot(embedding_weakness, weakness) / (
                    np.linalg.norm(embedding_weakness) * np.linalg.norm(weakness)
                )
                if cosine_sim > max_sim:
                    max_sim = cosine_sim
                    max_idx = i
            voyageai_sim_weaknesses.append(max_sim)
            generated_weakness_matchings_voyageai.append(
                {
                    'generated': generated_weakness,
                    'matched': weaknesses[max_idx],
                    'similarity': max_sim,
                }
            )

    metrics_raw['openai_sim_strengths'] = openai_sim_strengths
    metrics_raw['openai_sim_weaknesses'] = openai_sim_weaknesses
    metrics_raw['voyageai_sim_strengths'] = voyageai_sim_strengths
    metrics_raw['voyageai_sim_weaknesses'] = voyageai_sim_weaknesses
    metrics_raw['openai_strength'] = np.mean(openai_sim_strengths).item()
    metrics_raw['openai_weakness'] = np.mean(openai_sim_weaknesses).item()
    metrics_raw['voyageai_strength'] = np.mean(voyageai_sim_strengths).item()
    metrics_raw['voyageai_weakness'] = np.mean(voyageai_sim_weaknesses).item()
    metrics_raw['generated_strength_matchings_openai'] = (
        generated_strength_matchings_openai
    )
    metrics_raw['generated_weakness_matchings_openai'] = (
        generated_weakness_matchings_openai
    )
    metrics_raw['generated_strength_matchings_voyageai'] = (
        generated_strength_matchings_voyageai
    )
    metrics_raw['generated_weakness_matchings_voyageai'] = (
        generated_weakness_matchings_voyageai
    )
    return metrics_raw
