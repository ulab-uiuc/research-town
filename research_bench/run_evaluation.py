import argparse
import json
import logging
import os
from typing import Any, Dict, List, Optional

from metrics import compute_bertscore, compute_bleu, compute_gpt_metric, compute_rouge_l
from tqdm import tqdm
from utils import get_current_5q, single_agent_proposal_writing

from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ProposalWritingEnv
from research_town.utils.paper_collector import get_paper_introduction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_proposal_5q(
    authors: List[str], intros: List[str], keyword: str, id: int
) -> Optional[str]:
    """
    Generates a comprehensive research proposal based on the provided authors and existing proposals
    using the ProposalWritingEnv environment.

    Args:
        authors (List[str]): List of author names.
        intros (List[str]): List of existing introduction texts.

    Returns:
        Optional[str]: Generated proposal as a string if successful, else None.
    """

    config = Config('../configs')
    if os.path.exists(f'./profile_dbs/profile_{id}'):
        profile_db = ProfileDB(load_file_path=f'./profile_dbs/profile_{id}')
    else:
        profile_db = ProfileDB()
        profile_db.pull_profiles(names=authors, config=config)
        profile_db.save_to_json(f'./profile_dbs/profile_{id}')

    # Initialize other databases using default instances
    log_db = LogDB()
    progress_db = ProgressDB()
    paper_db = PaperDB()  # Assuming existing papers are handled elsewhere
    paper_db.pull_papers(num=3, domain=keyword)
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
        return str(proposal.content)
    else:
        logger.warning('Proposal generation returned no content.')
        return None


def process_paper(
    args: argparse.ArgumentParser,
    paper_key: str,
    paper_data: Dict[str, Any],
    id: int,
    intro_log_jsonl: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Processes a single paper to generate evaluations.

    Args:
        paper_key (str): The key identifier for the paper.
        paper_data (Dict[str, Any]): The data dictionary of the paper.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing evaluation results, or None if processing fails.
    """
    # try:
    arxiv_id = paper_data.get('arxiv_id')
    authors = paper_data.get('authors', [])
    references = paper_data.get('references', [])
    keyword = paper_data.get('keyword', '')

    if not arxiv_id:
        logger.warning(f'Missing arxiv_id for paper: {paper_key}')
        return None

    # Form the main paper URL
    main_paper_url = f'https://arxiv.org/pdf/{arxiv_id}'
    logger.info(f'Fetching introduction for main paper: {main_paper_url}')
    current_5q = None
    # Step 1: Get the paper introduction using the updated function
    if intro_log_jsonl:
        with open(intro_log_jsonl, 'r', encoding='utf-8') as infile:
            for line in infile:
                intro_data = json.loads(line)
                if intro_data.get('paper_key') == paper_key:
                    current_5q = intro_data.get('current_5q')
                    logger.info(f'Found current_5q for paper: {paper_key}')
                    break

    if not current_5q:
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
    intros = None
    if intro_log_jsonl:
        with open(intro_log_jsonl, 'r', encoding='utf-8') as infile:
            for line in infile:
                intro_data = json.loads(line)
                if intro_data.get('paper_key') == paper_key:
                    intros = intro_data.get('referenced_intros', None)
                    logger.info(f'Found referenced intros for paper: {paper_key}')
                    break
    if not intros:
        intros = []
        logger.info(f'No referenced intros found for paper: {paper_key}')
        for ref in references:
            print('ref', ref)
            external_ids = ref.get('externalIds', {})
            if not external_ids:
                continue
            print('external_ids', external_ids)
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

    # Optionally, you can use the collected intros for further processing
    # For example, passing them to get_proposal_5q or other functions
    # Currently, get_proposal_5q only uses authors and proposals
    # If intros are needed in get_proposal_5q, modify the function accordingly

    # Step 4: Generate proposal 5Q
    if args.test_single_agent:
        proposal_5q = single_agent_proposal_writing(
            intros=intros, model=args.single_agent_model
        )
    else:
        proposal_5q = get_proposal_5q(authors, intros, keyword, id)
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


def main(
    args: argparse.ArgumentParser,
    input_json: str,
    output_jsonl: str,
    intro_log_jsonl: str = '',
) -> None:
    """
    Main function to perform evaluation on all papers in the input JSON.

    Args:
        input_json (str): Path to the input JSON file.
        output_jsonl (str): Path to the output JSONL file.
    """
    # try:
    # Load input JSON
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = list(data.keys())
    logger.info(f'Found {len(papers)} papers to process.')

    # Initialize lists to store evaluation metrics
    bleu_scores = []
    rouge_l_scores = []
    gpt_metric_scores = []
    bert_scores = []
    num_lines = 0
    try:
        with open(output_jsonl, 'r', encoding='utf-8') as outfile:
            num_lines = sum(1 for line in outfile)
            papers = papers[num_lines:]
            logger.info(f'Skipping {num_lines} papers already processed.')
    except Exception as e:
        logger.error(f'Error reading output JSONL file: {e}')
        pass

    for id, paper_key in enumerate(
        tqdm(papers, desc='Processing papers'), start=1 + num_lines
    ):
        paper_data = data[paper_key]
        evaluation = process_paper(args, paper_key, paper_data, id, intro_log_jsonl)
        if evaluation:
            # Write the evaluation result as a JSON line
            with open(output_jsonl, 'a', encoding='utf-8') as outfile:
                outfile.write(json.dumps(evaluation) + '\n')
                outfile.flush()
            # Accumulate metrics for averaging
            bleu_scores.append(evaluation.get('bleu', 0.0))
            rouge_l_scores.append(evaluation.get('rouge_l', 0.0))
            bert_scores.append(evaluation.get('bert_score', 0.0))
            gpt_score = evaluation.get('gpt_metric_score')
            if gpt_score is not None:
                gpt_metric_scores.append(gpt_score)
        else:
            logger.warning(f'Skipping paper due to failed processing: {paper_key}')

    # Compute and log average metrics
    avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
    avg_rouge_l = sum(rouge_l_scores) / len(rouge_l_scores) if rouge_l_scores else 0.0
    avg_gpt_metric = (
        sum(gpt_metric_scores) / len(gpt_metric_scores) if gpt_metric_scores else 0.0
    )
    avg_bert_score = sum(bert_scores) / len(bert_scores) if bert_scores else 0.0

    logger.info(f'Average BLEU score: {avg_bleu:.4f}')
    logger.info(f'Average ROUGE-L score: {avg_rouge_l:.4f}')
    logger.info(f'Average GPT-based metric score: {avg_gpt_metric:.4f}')
    logger.info(f'Average BERTScore: {avg_bert_score:.4f}')


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
    parser.add_argument(
        '--intro_log',
        type=str,
        required=False,
        help='Path to the introduction log JSONL file.',
    )
    parser.add_argument(
        '--test-single-agent',
        action='store_true',
        help='If set, run a test for a single agent using sample introductions.',
    )
    parser.add_argument(
        '--single-agent-model',
        type=str,
        required=False,
        default='gpt-40-mini',
        help='Model name for the single agent test.',
    )
    args = parser.parse_args()

    main(args, args.input, args.output, args.intro_log)
