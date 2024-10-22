import os
from typing import List, Optional

from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ProposalWritingwithoutRAGEnv as ProposalWritingEnv
from research_town.utils.model_prompting import model_prompting


def write_proposal_researchtown(
    authors: List[str],
    intros: List[str],
    id: int,
    exclude_paper_titles: List[str] = [''],
) -> str:
    config = Config('../configs')
    if os.path.exists(f'./profile_dbs/profile_{id}'):
        profile_db = ProfileDB(load_file_path=f'./profile_dbs/profile_{id}')
    else:
        profile_db = ProfileDB()
        profile_db.pull_profiles(
            names=authors, config=config, exclude_paper_titles=exclude_paper_titles
        )
        profile_db.save_to_json(f'./profile_dbs/profile_{id}')

    # Initialize other databases using default instances
    log_db = LogDB()
    progress_db = ProgressDB()
    paper_db = PaperDB()  # Assuming existing papers are handled elsewhere
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
        raise ValueError('Failed to create leader agent')

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
        raise ValueError('Failed to generate proposal')


def write_proposal_single_agent(
    author: str, intros: List[str], id: int, exclude_paper_titles: List[str] = ['']
) -> str:
    config = Config('../configs')
    if os.path.exists(f'./profile_dbs/profile_{id}'):
        profile_db = ProfileDB(load_file_path=f'./profile_dbs/profile_{id}')
    else:
        profile_db = ProfileDB()
        profile_db.pull_profiles(
            names=[author], config=config, exclude_paper_titles=exclude_paper_titles
        )
        profile_db.save_to_json(f'./profile_dbs/profile_{id}')

    bio = profile_db.get(name=author)[0].bio

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
                    f'Introductions collect from some previous papers:\n{intros}\n\n'
                    'You are the only author of this paper. Please provide the five core questions contents for a brand new future research based on the above introductions.'
                    f'Your biography and persona is:\n{bio}'
                    'Please provide the five core questions contents based on the above introduction.'
                ),
            }
        ]
        response = model_prompting(config.param.base_llm, prompt, mode='TEST')
        if response and len(response) > 0 and len(response[0]) > 0:
            return response[0]
        else:
            raise ValueError('Received empty response from model_prompting for write_proposal_single_agent.')
    except Exception as e:
        raise ValueError(f'Error generating current_5q: {e}')


def extract_reference_proposal(intro: str, model: str = 'gpt-4o-mini') -> str:
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
            raise ValueError('Received empty response from model_prompting for extract_reference_proposal.')
    except Exception as e:
        raise ValueError(f'Error generating current_5q: {e}')


def write_proposal_author_only(
    authors: List[str], id: int, exclude_paper_titles: List[str] = ['']
) -> str:
    config = Config('../configs')
    profile_db_path = f'./profile_dbs/profile_{id}'

    if os.path.exists(profile_db_path):
        profile_db = ProfileDB(load_file_path=profile_db_path)
    else:
        profile_db = ProfileDB()
        profile_db.pull_profiles(
            names=authors, config=config, exclude_paper_titles=exclude_paper_titles
        )
        profile_db.save_to_json(profile_db_path)
    profiles = []
    for author in authors:
        print('author', author)

        profile = profile_db.get(name=author)[0]
        profiles.append(profile)
    bios = '\n'.join([profile.bio for profile in profiles])
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
                    f'Author biographies and personas:\n{bios}\n\n'
                    'You are the authors of this paper. Please provide the five core questions contents for a brand new future research based on the above biographies.'
                ),
            }
        ]
        response = model_prompting(config.param.base_llm, prompt, mode='TEST')
        if response and len(response) > 0 and len(response[0]) > 0:
            return response[0]
        else:
            raise ValueError('Received empty response from model_prompting for write_proposal_author_only.')
    except Exception as e:
        raise ValueError(f'Error generating current_5q: {e}')


def write_proposal_citation_only(
    intros: List[str], id: int, exclude_paper_titles: List[str] = ['']
) -> str:
    raise NotImplementedError


def write_proposal_author_citation(
    authors: List[str],
    intros: List[str],
    id: int,
    exclude_paper_titles: List[str] = [''],
) -> str:
    raise NotImplementedError


def write_proposal(
    mode: str,
    authors: List[str],
    intros: List[str],
    id: int,
    exclude_paper_titles: List[str],
) -> str:
    if mode == 'author-only':
        return write_proposal_author_only(
            authors=authors, id=id, exclude_paper_titles=exclude_paper_titles
        )
    elif mode == 'citation-only':
        return write_proposal_citation_only(
            intros, id, exclude_paper_titles=exclude_paper_titles
        )
    elif mode == 'author-citation':
        return write_proposal_author_citation(
            authors, intros, id, exclude_paper_titles=exclude_paper_titles
        )
    elif mode == 'textgnn':
        return write_proposal_researchtown(
            authors, intros, id, exclude_paper_titles=exclude_paper_titles
        )
    else:
        raise ValueError(f'Invalid proposal writing mode: {mode}')
