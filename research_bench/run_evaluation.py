#!/usr/bin/env python3
"""
run_evaluation.py

This script automates the evaluation of tool-augmented Large Language Models (LLMs) as conversational AI agents.
It processes a JSON file containing research papers, extracts necessary information, generates evaluations
based on core questions, and computes evaluation metrics to assess the performance of the models.

Features:
1. Extracts the introduction section from each paper's PDF.
2. Generates five core research questions based on the introduction using an LLM.
3. Generates a proposal based on the authors and existing proposals using an LLM.
4. Computes BLEU, ROUGE-L, and a custom GPT-based metric to evaluate the alignment between generated questions and proposals.
5. Outputs per-paper results to a JSONL file and prints average evaluation metrics.

Usage:
    python run_evaluation.py --input path_to_input_json --output path_to_output_jsonl

Dependencies:
    - tqdm
    - nltk
    - rouge-score
    - requests
    - PyPDF2
    - research_town.utils.model_prompting (custom module)
    - openai

Ensure that the OpenAI API key is set in the environment if using OpenAI's models.
"""

import argparse
import json
import logging
import os
from typing import Any, Dict, List, Optional

import nltk
from bert_score import score
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer
from tqdm import tqdm

from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ProposalWritingEnv
from research_town.utils.agent_prompter import model_prompting
from research_town.utils.paper_collector import get_paper_introduction

# Initialize NLTK resources
nltk.download('punkt')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_current_5q(intro: str) -> Optional[str]:
    """
    Generates the five core research questions based on the introduction text using an LLM.

    Args:
        intro (str): Introduction text of the paper.

    Returns:
        Optional[str]: Generated five core questions as a string.
    """
    try:
        prompt = [
            {
                'role': 'user',
                'content': (
                    'Here is a high-level summarized insight of a research field Machine Learning.\n\n'
                    'Here are the five core questions:\n\n'
                    '[Question 1] - What is the problem?\n\n'
                    'Formulate the specific research question you aim to address. Only output one question and do not include any more information.\n\n'
                    '[Question 2] - Why is it interesting and important?\n\n'
                    'Explain the broader implications of solving this problem for the research community.\n'
                    'Discuss how such paper will affect the future research.\n'
                    'Discuss how addressing this question could advance knowledge or lead to practical applications.\n\n'
                    '[Question 3] - Why is it hard?\n\n'
                    'Discuss the challenges and complexities involved in solving this problem.\n'
                    'Explain why naive or straightforward approaches may fail.\n'
                    'Identify any technical, theoretical, or practical obstacles that need to be overcome. MAKE IT CLEAR.\n\n'
                    "[Question 4] - Why hasn't it been solved before?\n\n"
                    'Identify gaps or limitations in previous research or existing solutions.\n'
                    'Discuss any barriers that have prevented this problem from being solved until now.\n'
                    'Explain how your approach differs from or improves upon prior work. MAKE IT CLEAR.\n\n'
                    '[Question 5] - What are the key components of my approach and results?\n\n'
                    'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use.\n'
                    'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                    f'Introduction:\n{intro}\n\n'
                    'Please provide the five core questions contents based on the above introduction.'
                ),
            }
        ]
        response = model_prompting('gpt-4o-mini', prompt, mode='TEST')
        if response and len(response) > 0 and len(response[0]) > 0:
            return response[0]
        else:
            logger.warning(
                'Received empty response from model_prompting for current_5q.'
            )
            return None
    except Exception as e:
        logger.error(f'Error generating current_5q: {e}')
        return None


def get_proposal_5q(authors: List[str], intros: List[str]) -> Optional[str]:
    """
    Generates a comprehensive research proposal based on the provided authors and existing proposals
    using the ProposalWritingEnv environment.

    Args:
        authors (List[str]): List of author names.
        intros (List[str]): List of existing introduction texts.

    Returns:
        Optional[str]: Generated proposal as a string if successful, else None.
    """
    try:
        # Initialize ProfileDB and add profiles based on the authors

        config = Config('../configs')
        profile_db = ProfileDB()
        if os.path.exists('./profiles'):
            profile_db.load_from_json('./profiles')
        else:
            profile_db.pull_profiles(names=authors, config=config)
            profile_db.save_to_json('./profiles')
        # Initialize other databases using default instances
        log_db = LogDB()
        progress_db = ProgressDB()
        paper_db = PaperDB()  # Assuming existing papers are handled elsewhere
        paper_db.pull_papers(num=2, domain='multi-agent')
        # Initialize ProposalWritingEnv with the required databases and configuration
        agent_manager = AgentManager(config=config, profile_db=profile_db)
        env = ProposalWritingEnv(
            name='proposal_writing',
            log_db=log_db,
            progress_db=progress_db,
            paper_db=paper_db,
            config=config,
            agent_manager=agent_manager,
        )
        logger.info('Initialized ProposalWritingEnv.')

        # Create a leader agent (assuming `create_leader` requires a profile)
        leader_profile = profile_db.get(name=authors[0])[0]
        print('leader_profile', leader_profile)
        leader = agent_manager.create_agent(leader_profile, role='leader')
        if not leader_profile:
            logger.error('No valid leader profile found.')
            return None
        logger.info('Created leader agent for profile')

        # Prepare the context from existing proposals
        # Assuming that the context should be a list of proposal strings
        env.on_enter(
            leader=leader,
            contexts=intros,
        )
        logger.info('Entered ProposalWritingEnv with provided proposals as context.')

        # Run the environment to generate the proposal
        run_result = env.run()
        if run_result is not None:
            for progress, agent in run_result:
                # Process progress and agent if needed
                pass
        logger.info('Ran ProposalWritingEnv.')

        # Exit the environment and retrieve the generated proposal
        exit_status, exit_dict = env.on_exit()
        proposal = exit_dict.get('proposal')
        if proposal and proposal.content:
            logger.info('Successfully generated proposal.')
            return proposal.content
        else:
            logger.warning('Proposal generation returned no content.')
            return None

    except Exception as e:
        logger.error(f'Error generating proposal_5q: {e}')
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
        reference_tokens = nltk.word_tokenize(reference.lower())
        hypothesis_tokens = nltk.word_tokenize(hypothesis.lower())
        smoothie = SmoothingFunction().method4
        bleu_score = sentence_bleu(
            [reference_tokens], hypothesis_tokens, smoothing_function=smoothie
        )
        return bleu_score
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
        return rouge_l_f1
    except Exception as e:
        logger.error(f'Error computing ROUGE-L score: {e}')
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
        return F1.mean().item()
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
                    'Evaluate the following two sets of five core research questions for alignment.\n\n'
                    'Current 5Q:\n'
                    f'{current_5q}\n\n'
                    'Proposal 5Q:\n'
                    f'{proposal_5q}\n\n'
                    'Please provide a similarity score 0 or 1, where 1 means the two proposals somewhat alignment to each other, especially the method part, and 0 means no alignment. Only output the score, without any additional information.'
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


def process_paper(
    paper_key: str, paper_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Processes a single paper to generate evaluations.

    Args:
        paper_key (str): The key identifier for the paper.
        paper_data (Dict[str, Any]): The data dictionary of the paper.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing evaluation results, or None if processing fails.
    """
    try:
        arxiv_id = paper_data.get('arxiv_id')
        authors = paper_data.get('authors', [])
        references = paper_data.get('references', [])

        if not arxiv_id:
            logger.warning(f'Missing arxiv_id for paper: {paper_key}')
            return None

        # Form the main paper URL
        main_paper_url = f'https://arxiv.org/pdf/{arxiv_id}'
        logger.info(f'Fetching introduction for main paper: {main_paper_url}')

        # Step 1: Get the paper introduction using the updated function
        intro = get_paper_introduction(main_paper_url)
        if not intro:
            logger.warning(f'Introduction not found for paper: {paper_key}')
            return None

        # Step 2: Generate current 5Q
        current_5q = get_current_5q(intro)
        if not current_5q:
            logger.warning(f'current_5q generation failed for paper: {paper_key}')
            return None
        logger.info(f'Generated current_5q for paper: {current_5q}')

        # Step 3: Extract proposals from references with ArXiv externalIds
        proposals = []
        intros = []
        for ref in references:
            external_ids = ref.get('externalIds', {})
            arxiv_ref_id = external_ids.get('ArXiv')
            if arxiv_ref_id:
                ref_url = f'https://arxiv.org/pdf/{arxiv_ref_id}'
                logger.info(f'Fetching introduction for referenced paper: {ref_url}')
                ref_intro = get_paper_introduction(ref_url)
                if ref_intro:
                    intros.append(ref_intro)
                else:
                    logger.warning(
                        f'Introduction not found for referenced paper: {ref_url}'
                    )
            # Collect proposal titles regardless of ArXiv presence
            proposal_title = ref.get('title', '')
            if proposal_title:
                proposals.append(proposal_title)

        # Optionally, you can use the collected intros for further processing
        # For example, passing them to get_proposal_5q or other functions
        # Currently, get_proposal_5q only uses authors and proposals
        # If intros are needed in get_proposal_5q, modify the function accordingly

        # Step 4: Generate proposal 5Q
        proposal_5q = get_proposal_5q(authors, intros)
        if not proposal_5q:
            logger.warning(f'proposal_5q generation failed for paper: {paper_key}')
            return None

        # Step 5: Compute evaluation metrics
        bleu = compute_bleu(current_5q, proposal_5q)
        rouge_l = compute_rouge_l(current_5q, proposal_5q)
        gpt_metric = compute_gpt_metric(current_5q, proposal_5q)
        bert_score = compute_bertscore(current_5q, proposal_5q)

        evaluation_result = {
            'paper_key': paper_key,
            'current_5q': current_5q,
            'proposal_5q': proposal_5q,
            'referenced_intros': intros,  # Optional: Include referenced intros in the result
            'bleu': bleu,
            'rouge_l': rouge_l,
            'gpt_metric_score': gpt_metric,
            'bert_score': bert_score,
        }

        return evaluation_result

    except Exception as e:
        logger.error(f'Error processing paper {paper_key}: {e}')
        return None


def main(input_json: str, output_jsonl: str) -> None:
    """
    Main function to perform evaluation on all papers in the input JSON.

    Args:
        input_json (str): Path to the input JSON file.
        output_jsonl (str): Path to the output JSONL file.
    """
    try:
        # Load input JSON
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        papers = data.keys()
        logger.info(f'Found {len(papers)} papers to process.')

        # Initialize lists to store evaluation metrics
        bleu_scores = []
        rouge_l_scores = []
        gpt_metric_scores = []
        bert_scores = []

        # Open output JSONL file
        with open(output_jsonl, 'w', encoding='utf-8') as outfile:
            # Iterate over each paper with a progress bar
            for paper_key in tqdm(papers, desc='Processing papers'):
                paper_data = data[paper_key]
                evaluation = process_paper(paper_key, paper_data)
                if evaluation:
                    # Write the evaluation result as a JSON line
                    outfile.write(json.dumps(evaluation) + '\n')

                    # Accumulate metrics for averaging
                    bleu_scores.append(evaluation.get('bleu', 0.0))
                    rouge_l_scores.append(evaluation.get('rouge_l', 0.0))
                    bert_scores.append(evaluation.get('bert_score', 0.0))
                    gpt_score = evaluation.get('gpt_metric_score')
                    if gpt_score is not None:
                        gpt_metric_scores.append(gpt_score)
                else:
                    logger.warning(
                        f'Skipping paper due to failed processing: {paper_key}'
                    )

        # Compute and log average metrics
        avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
        avg_rouge_l = (
            sum(rouge_l_scores) / len(rouge_l_scores) if rouge_l_scores else 0.0
        )
        avg_gpt_metric = (
            sum(gpt_metric_scores) / len(gpt_metric_scores)
            if gpt_metric_scores
            else 0.0
        )
        avg_bert_score = sum(bert_scores) / len(bert_scores) if bert_scores else 0.0

        logger.info(f'Average BLEU score: {avg_bleu:.4f}')
        logger.info(f'Average ROUGE-L score: {avg_rouge_l:.4f}')
        logger.info(f'Average GPT-based metric score: {avg_gpt_metric:.4f}')
        logger.info(f'Average BERTScore: {avg_bert_score:.4f}')

    except Exception as e:
        logger.error(f'An error occurred in the main execution: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Automated Evaluation of Tool-Augmented LLMs as Conversational AI Agents'
    )
    parser.add_argument(
        '--input', type=str, required=True, help='Path to the input JSON file.'
    )
    parser.add_argument(
        '--output', type=str, required=True, help='Path to the output JSONL file.'
    )
    args = parser.parse_args()

    main(args.input, args.output)
