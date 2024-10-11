from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ProposalWritingEnv
from research_town.utils.paper_collector import get_paper_introduction
from typing import List, Optional
import logging
import os
from typing import Optional
from research_town.utils.model_prompting import model_prompting


def write_proposal_researchtown(
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

    # Create a leader agent (assuming `create_leader` requires a profile)
    leader_profile = profile_db.get(name=authors[0])[0]
    print('leader_profile', leader_profile)
    leader = agent_manager.create_agent(leader_profile, role='leader')
    if not leader_profile:
        return None

    # Prepare the context from existing proposals
    # Assuming that the context should be a list of proposal strings
    env.on_enter(
        leader=leader,
        contexts=intros,
    )

    # Run the environment to generate the proposal
    run_result = env.run()
    if run_result is not None:
        for progress, agent in run_result:
            # Process progress and agent if needed
            pass

    # Exit the environment and retrieve the generated proposal
    exit_status, exit_dict = env.on_exit()
    proposal = exit_dict.get('proposal')
    if proposal and proposal.content:
        return str(proposal.content)
    else:
        return None


def write_proposal_baseline(intro: str, model: str = 'gpt-4o-mini') -> Optional[str]:
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
        response = model_prompting(model, prompt, mode='TEST')
        if response and len(response) > 0 and len(response[0]) > 0:
            return response[0]
        else:
            print('Received empty response from model_prompting for current_5q.')
            return None
    except Exception as e:
        print(f'Error generating current_5q: {e}')
        return None
