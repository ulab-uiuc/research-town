from typing import List
import random
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
    log_db = LogDB(config=config.database)
    progress_db = ProgressDB(config=config.database)
    paper_db = PaperDB(config=config.database)
    profile_db = ProfileDB(config=config.database)
    agent_manager = AgentManager(config=config.param, profile_db=profile_db)

    env = ProposalWritingEnv(
        name='proposal_writing',
        log_db=log_db,
        progress_db=progress_db,
        paper_db=paper_db,
        config=config,
        agent_manager=agent_manager,
    )

    leader_profile = profiles[0]
    leader = agent_manager.create_agent(leader_profile, role='leader')
    members = []
    for member_profile in profiles[1:]:
        member = agent_manager.create_agent(member_profile, role='member')
        members.append(member)
    if not leader_profile:
        raise ValueError('Failed to create leader agent')

    ref_contents = [ref for ref in ref_contents if ref is not None]
    assert None not in ref_contents
    env.on_enter(
        leader=leader,
        members=members,
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
    proposal = exit_dict.get('proposals')[0]
    if proposal and proposal.content:
        return str(proposal.content)
    else:
        raise ValueError('Failed to generate proposal')


def write_proposal_zero_shot(config: Config) -> str:
    prompt = [
        {
            'role': 'user',
            'content': (
                'You are a AI researcher. Here is a high-level summarized insight of a research field Machine Learning.\n\n'
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
                'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use. But you must include these in one paragraph and not use subtitles.\n'
                'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                'Please provide the five core questions contents for a brand new future research that you think are the most promising one.'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt)[0]
    return response


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
                'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use. But you must include these in one paragraph and not use subtitles.\n'
                'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                f'Author biographies and personas:\n{bio_strs}\n\n'
                'You are the profiles of this paper. Please provide the five core questions contents for a brand new future research based on the above biographies.'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)[0]
    return response


def write_proposal_with_only_citations(ref_contents: List[str], config: Config) -> str:
    random.seed(0)
    random.shuffle(ref_contents)
    ref_strs = ''
    for idx, ref in enumerate(ref_contents):
        if ref is None:
            continue
        ref_strs += f'paper {idx + 1}. {ref}\n\n'

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
                'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use. But you must include these in one paragraph and not use subtitles.\n'
                'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                f'Contents collect from cited papers:\n{ref_strs}\n\n'
                'Please brainstorm a following proposal with the given format.'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)[0]
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
    response = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)[0]
    return response


def write_proposal_sakana_ai_scientist(
    ref_contents: List[str], config: Config, num_reflections: int = 5
) -> str:
    ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])

    # Prompt for the initial idea generation
    idea_first_prompt = f"""
You are an ambitious AI researcher who is looking to publish a paper that will contribute significantly to the field.

Here are the summarized contents collected from cited papers:

{ref_strs}

Come up with the next impactful and creative idea for research experiments and directions you can feasibly investigate with the code provided.
Note that you will not have access to any additional resources or datasets.
Make sure any idea is not overfit the specific training dataset or model, and has wider significance.

Respond in the following format:

THOUGHT:
<THOUGHT>

NEW IDEA:

[Question 1] - What is the problem?

Formulate the specific research question you aim to address. Only output one question and do not include any more information.

[Question 2] - Why is it interesting and important?

Explain the broader implications of solving this problem for the research community.

Discuss how such a paper will affect future research.

Discuss how addressing this question could advance knowledge or lead to practical applications.

[Question 3] - Why is it hard?

Discuss the challenges and complexities involved in solving this problem.

Explain why naive or straightforward approaches may fail.

Identify any technical, theoretical, or practical obstacles that need to be overcome.

[Question 4] - Why hasn't it been solved before?

Identify gaps or limitations in previous research or existing solutions.

Discuss any barriers that have prevented this problem from being solved until now.

Explain how your approach differs from or improves upon prior work.

[Question 5] - What are the key components of my approach and results?

Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use.

Describe the expected outcomes.

In <THOUGHT>, first briefly discuss your intuitions and motivations for the idea. Detail your high-level plan, necessary design choices and ideal outcomes of the experiments. Justify how the idea is different from the existing ones.

Please DO NOT repeat the instructions. Instead, fill in the 5 questions to form your proposal.

You will have {num_reflections} rounds to iterate on the idea, but do not need to use them all.
"""

    idea_reflection_prompt = """
Round {current_round}/{num_reflections}.

Carefully consider the quality, novelty, and feasibility of the proposal you just created.

Include any other factors that you think are important in evaluating the proposal.

Ensure the proposal is clear and concise, and follows the correct format.

Do not make things overly complicated.

In the next attempt, try and refine and improve your proposal.

Stick to the spirit of the original idea unless there are glaring issues.
Respond in the same format(THOUGHT, NEW IDEA composing of 5 questions) as before.

If there is nothing to improve, simply repeat the previous proposal exactly and include "I am done" at the end.

ONLY INCLUDE "I am done" IF YOU ARE MAKING NO MORE CHANGES.

Please provide the updated proposal in the same format as before.
"""

    conversation = []

    conversation.append({'role': 'user', 'content': idea_first_prompt})

    response = model_prompting(config.param.base_llm, conversation, max_token_num=config.param.max_token_num)[0]
    conversation.append({'role': 'assistant', 'content': response})

    for current_round in range(1, num_reflections + 1):
        formatted_reflection_prompt = idea_reflection_prompt.format(
            current_round=current_round, num_reflections=num_reflections
        )
        conversation.append({'role': 'user', 'content': formatted_reflection_prompt})

        response = model_prompting(config.param.base_llm, conversation, max_token_num=config.param.max_token_num)[0]
        
        conversation.append({'role': 'assistant', 'content': response})

        if 'I am done' in response:
            break

    if 'I am done' in conversation[-1]['content'] and "[Question 1]" not in conversation[-1]['content']:
        if 'NEW IDEA:' in conversation[-2]['content']:
            return conversation[-2]['content'].split('NEW IDEA:')[1]
        else:
            return conversation[-2]['content']
    else:
        if 'NEW IDEA:' in conversation[-1]['content']:
            return conversation[-1]['content'].split('NEW IDEA:')[1].split('I am done')[0]
        else:
            return conversation[-1]['content'].split('I am done')[0]

def write_proposal_debug(profiles: List[Profile], ref_contents: List[str], config: Config) -> str:
    random.seed(0)
    random.shuffle(ref_contents)
    ref_strs = ''
    for idx, ref in enumerate(ref_contents):
        if ref is None:
            continue
        ref_strs += f'paper {idx + 1}. {ref}\n'
    profile_str = '\n'.join([profile.bio for profile in profiles])

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
                'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use. But you must include these in one paragraph and not use subtitles.\n'
                'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                f'Contents collect from cited papers:\n{ref_strs}\n\n'
                'Please brainstorm a following proposal with the given format.'
            ),
        }
    ]
    generated_5q = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)[0]
    # delete all things after [Question 5]
    generated_4q = generated_5q.split('[Question 5]')[0]

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
                'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use. But you must include these in one paragraph and not use subtitles.\n'
                'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                'This is the generated [Question 1] to [Question 4] based on the citation papers.\n'
                f'{generated_4q}\n\n'
                'You have a group of researchers who the bio is as follows:\n'
                f'{profile_str}\n\n'
                'When you are generating [Question 5], you can think how to do the thing based on your bio information.\n'
                'Please brainstorm a following proposal with the given format. You should still start with [Question 1] to [Question 5]. But the content from [Question 1] to [Question 4] is already given and you just copy them as part of the output.'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)[0]
    return response

import random
from typing import List
from voyageai import Client

def fuse_questions(fiveq_candidates: List[str], ref_strs: str, config: Config) -> str:
    fiveq_candidate_strs = '\n'.join([f'Proposal {idx + 1}. {candidate}' for idx, candidate in enumerate(fiveq_candidates)])
    prompt = [
        {
            'role': 'user',
            'content': (
                f"Here is a high-level summarized insight of a research field: Machine Learning.\n\n"
                f"Here are the five core questions to consider:\n\n"
                f"[Question 1] - What is the problem?\n"
                f"[Question 2] - Why is it interesting and important?\n"
                f"[Question 3] - Why is it hard?\n"
                f"[Question 4] - Why hasn't it been solved before?\n"
                f"[Question 5] - What are the key components of my approach and results?\n\n"
                f"Multiple proposals have been generated for the above questions:\n{fiveq_candidate_strs}\n\n"
                f"Additionally, here are related references collected from papers:\n{ref_strs}\n\n"
                f"Your task is to summarize and select the key insights that are suitable from these proposals.\n"
                f"1. Identify shared themes and common points among the proposals.\n"
                f"2. Highlight and select any valuable perspectives or contrasting elements and combine them into one proposal.\n"
                f"3. Provide a concise proposal for each question based on the proposal candidates.\n\n"
                f"Output the result in the provided five question format.\n\n"
                f"Ensure the generated proposal is clear, concise, and avoids repeating full proposals verbatim."
            ),
        }
    ]
    summarized_response = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)
    return summarized_response[0].strip()


def write_proposal_fake_researchtown(
    profiles: List[Profile],
    ref_contents: List[str],
    config: Config,
) -> str:
    random.seed(0)
    random.shuffle(ref_contents)

    fiveq_candidates = []
    for profile in profiles:
        ref_contents = [ref for ref in ref_contents if ref is not None]
        ref_strs = '\n'.join([f'paper {idx + 1}. {ref}' for idx, ref in enumerate(ref_contents) if ref])
        
        prompt = [
            {
                'role': 'user',
                'content': 'Who are you?',
            },
            {
                'role': 'assistant',
                'content': profile.bio,
            },
            {
                'role': 'user',
                'content': (
                    "You need to write a research proposal for a paper in the field of Machine Learning.\n\n"
                    "Here is a high-level summarized insight of a research field Machine Learning.\n\n"
                    "Here are the five core questions:\n\n"
                    "[Question 1] - What is the problem?\n\n"
                    "Formulate the specific research question you aim to address.\n"
                    "Only output one question and do not include any more information.\n"
                    "Rely on the related papers to generate the question, do not rely on your previous experience.\n\n"
                    "[Question 2] - Why is it interesting and important?\n\n"
                    "Explain the broader implications of solving this problem for the research community.\n"
                    "Discuss how such paper will affect the future research.\n"
                    "Discuss how addressing this question could advance knowledge or lead to practical applications.\n\n"
                    "Rely on the related papers to generate the question, do not rely on your previous experience.\n\n"
                    "[Question 3] - Why is it hard?\n\n"
                    "Discuss the challenges and complexities involved in solving this problem.\n"
                    "Explain why naive or straightforward approaches may fail.\n"
                    "Identify any technical, theoretical, or practical obstacles that need to be overcome. MAKE IT CLEAR.\n\n"
                    "Rely on the related papers to generate the question, do not rely on your previous experience.\n\n"
                    "[Question 4] - Why hasn't it been solved before?\n\n"
                    "Identify gaps or limitations in previous research or existing solutions.\n"
                    "Discuss any barriers that have prevented this problem from being solved until now.\n"
                    "Explain how your approach differs from or improves upon prior work. MAKE IT CLEAR.\n\n"
                    "Rely on the related papers to generate the question, do not rely on your previous experience.\n\n"
                    '[Question 5] - What are the key components of my approach and results?\n\n'
                    'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use. But you must include these in one paragraph and not use subtitles.\n'
                    'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                    "You should rely on both the related papers and your profile to generate the question. Typically, some metrics, datasets or detailed experimental design can be transfered to this new proposal.\n\n"
                    f'Contents collect from cited papers:\n{ref_strs}\n\n'
                    'Please brainstorm a following proposal with the given format.'
                ),
            }
        ]
        fiveq_response = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)[0]
        fiveq_candidates.append(fiveq_response)

    fused_fiveq = fuse_questions(fiveq_candidates, ref_strs, config)
    return fused_fiveq



def write_proposal(
    mode: str,
    profiles: List[Profile],
    ref_contents: List[str],
    config: Config,
    target_paper_title: str,
) -> str:
    if mode == 'zero_shot':
        return write_proposal_zero_shot(config=config)
    elif mode == 'author_only':
        return write_proposal_with_only_profiles(profiles=profiles, config=config)
    elif mode == 'citation_only':
        return write_proposal_with_only_citations(
            ref_contents=ref_contents, config=config,
        )
    elif mode == 'author_citation':
        return write_proposal_with_profiles_and_citations(
            profiles=profiles, ref_contents=ref_contents, config=config
        )
    elif mode == 'research_town':
        return write_proposal_researchtown(
            profiles=profiles, ref_contents=ref_contents, config=config
        )
    elif mode == 'sakana_ai_scientist':
        return write_proposal_sakana_ai_scientist(
            ref_contents=ref_contents, config=config, num_reflections=5
        )
    elif mode == 'debug':
        return write_proposal_debug(
            profiles=profiles, ref_contents=ref_contents, config=config,
        )
    elif mode == 'fake_research_town':
        return write_proposal_fake_researchtown(
            profiles=profiles, ref_contents=ref_contents, config=config
        )
    else:
        raise ValueError(f'Invalid proposal writing mode: {mode}')
