from typing import List

from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.data import Profile
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ProposalWritingwithoutRAGEnv as ProposalWritingEnv
from research_town.utils.model_prompting import model_prompting


def write_proposal_researchtown(
    profiles: List[Profile],
    ref_contents: List[str],
    config: Config,
) -> str:
    log_db = LogDB()
    progress_db = ProgressDB()
    paper_db = PaperDB()
    profile_db = ProfileDB()
    agent_manager = AgentManager(config=config, profile_db=profile_db)

    env = ProposalWritingEnv(
        name='proposal_writing',
        log_db=log_db,
        progress_db=progress_db,
        paper_db=paper_db,
        config=config,
        agent_manager=agent_manager,
    )

    leader_profile = profile_db.get(name=profiles[0].name)[0]
    print('leader_profile', leader_profile)
    leader = agent_manager.create_agent(leader_profile, role='leader')
    if not leader_profile:
        raise ValueError('Failed to create leader agent')

    env.on_enter(
        leader=leader,
        contexts=ref_contents,
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


def write_proposal_with_only_profiles(profiles: List[Profile], config: Config) -> str:
    bio_strs = '\n'.join([profile.bio for profile in profiles])

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
                f'Author biographies and personas:\n{bio_strs}\n\n'
                'You are the profiles of this paper. Please provide the five core questions contents for a brand new future research based on the above biographies.'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt)[0]
    return response


def write_proposal_with_only_citations(ref_contents: List[str], config: Config) -> str:
    ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])

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
                f'Contents collect from cited papers:\n{ref_strs}\n\n'
                'Please provide the five core questions contents based on the above cited contents.'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt)[0]
    return response


def write_proposal_with_profiles_and_citations(
    profiles: List[Profile], ref_contents: List[str], config: Config
) -> str:
    bio_strs = '\n'.join([profile.bio for profile in profiles])
    ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])

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
                f'Contents collect from cited papers:\n{ref_strs}\n\n'
                f'Author biographies and personas:\n{bio_strs}\n\n'
                'Based on the above biographies and cited paper contents, please provide the five core questions contents for a brand new future research.'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt)[0]
    return response


def write_predicted_proposal(
    mode: str,
    profiles: List[Profile],
    ref_contents: List[str],
    config: Config,
) -> str:
    if mode == 'author_only':
        return write_proposal_with_only_profiles(profiles=profiles, config=config)
    elif mode == 'citation_only':
        return write_proposal_with_only_citations(
            ref_contents=ref_contents, config=config
        )
    elif mode == 'author_citation':
        return write_proposal_with_profiles_and_citations(
            profiles=profiles, ref_contents=ref_contents, config=config
        )
    elif mode == 'textgnn':
        return write_proposal_researchtown(
            profiles=profiles, ref_contents=ref_contents, config=config
        )
    else:
        raise ValueError(f'Invalid proposal writing mode: {mode}')


def write_reference_proposal(intro: str, config: Config) -> str:
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
    response = model_prompting(config.param.base_llm, prompt)[0]
    return response
