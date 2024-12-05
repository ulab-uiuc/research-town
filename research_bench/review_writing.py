"""
Review Writing Process Evaluation
Input:   Real-world Papers
Process: Match Reviewers to Papers with Similar Interests
         Evaluate Reviewers' Reviews using Similarity Metrics
Output:  Reviewers' Similarity Scores
"""

from typing import List, Tuple, Dict, Any, Union

from litellm import token_counter
from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.data import Profile, Proposal, Review, MetaReview
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.utils.model_prompting import model_prompting
from research_town.envs import ReviewWritingEnv
from voyageai.client import Client

def write_review_research_town(
    paper_content: str, profiles_reviewers: List[Profile], ref_contents: List[str], config: Config
) -> Tuple[str, str, List[float], Dict[str, Dict[str, Any]]]:
    log_db = LogDB(config=config.database)
    progress_db = ProgressDB(config=config.database)
    paper_db = PaperDB(config=config.database)
    profile_db = ProfileDB(config=config.database)
    agent_manager = AgentManager(config=config.param, profile_db=profile_db)

    env = ReviewWritingEnv(
        name='review_writing',
        log_db=log_db,
        progress_db=progress_db,
        paper_db=paper_db,
        config=config,
        agent_manager=agent_manager,
    )

    # leader_profile = profile_db.get(name=profiles[0].name)[0]
    leader_profile = profiles_reviewers[0]

    # print('leader_profile', leader_profile)
    leader = agent_manager.create_agent(leader_profile, role='leader')
    if not leader_profile:
        raise ValueError('Failed to create leader agent')
    
    top_k = 5
    
    reviewers = [agent_manager.create_agent(profile, role='reviewer') for profile in profiles_reviewers[0:top_k]]

    ref_contents = [ref if ref else '' for ref in ref_contents]

    env.on_enter(
        leader=leader,
        chair=None,
        reviewers=reviewers,
        proposals=[Proposal(content=paper_content, citations=ref_contents)],
    )

    run_result = env.run()

    strength: str = ''
    weakness: str = ''
    scores: List[float] = []

    review_per_reviewer = {}

    if run_result is not None:
        for progress, agent in run_result:
            if isinstance(progress, Review):
                scores.append(progress.score)
                agent_name = agent.profile.name
                strength = progress.strength
                weakness = progress.weakness
                review_per_reviewer[agent_name] = {
                    'strength': strength,
                    'weakness': weakness,
                    'score': progress.score
                }
                
            if isinstance(progress, MetaReview):
                strength = progress.strength
                weakness = progress.weakness

    exit_status, exit_dict = env.on_exit()
    s_meta_review = f"{exit_dict.get('metareviews', '')}"
    return strength, weakness, scores, review_per_reviewer

# Baselines
def write_review_zero_shot(
    paper_content: str, config: Config
) -> Tuple[str, str, List[float]]:
    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the paper:\n'
                f'{paper_content}\n'
                "Please write a review of the paper based on the introduction. You should write a paragraph of approximately 200 words.\n"
                'You should only write about the strengths of the paper. It should be 200 words long.\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    strength = response

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the paper:\n'
                f'{paper_content}\n'
                "Please write a review of the paper based on the introduction. You should write a paragraph of approximately 200 words.\n"
                'You should only write about the weaknesses of the paper. It should be 200 words long.\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    weakness = response

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the strength of the paper:\n'
                f'{strength}\n'
                'Here is the weakness of the paper:\n'
                f'{weakness}\n'
                "Please rate the overall quality of the paper on a scale of 1 to 10. 1 is the lowest score while 10 is the highest score.\n"
                "You should just provide one number as the score and nothing else.\n"
                f"Your score is: "
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    score_options = ['10', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    score = 0
    for score_option in score_options:
        if score_option in response:
            score = int(score_option)

    return strength, weakness, [score]

def write_review_with_only_profiles(
    paper_content: str, profiles_reviewers: List[Profile], config: Config
) -> Tuple[str, str, List[float]]:
    bio_strs = '\n'.join([profile.bio for profile in profiles_reviewers])
    strengths: List[str] = []
    weaknesses: List[str] = []
    scores: List[float] = []

    profiles_reviewers = profiles_reviewers[:5]
    
    for profile in profiles_reviewers:
        bio_str = profile.bio
        token_input_count = 0
        token_output_count = 0
        prompt = [
            {
                'role': 'user',
                'content': (
                    'Here is your profile:\n'
                    f'{bio_str}\n'
                    'Here is the paper:\n'
                    f'{paper_content}\n'
                    "Please write a review of the paper based on the introduction and authors' profiles. You should write a paragraph of approximately 200 words.\n"
                    'You should only write about the strengths of the paper. It should be 200 words long.\n'
                ),
            }
        ]
        response = model_prompting(
            config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
        )[0]
        # write prompt[0]['content'], bio_str, paper_content to json indent 4
        # import time
        # import json
        # with open(f'./{time.time()}.json', 'w') as f:
        #     json.dump({'prompt': prompt[0]['content'], 'bio': bio_str, 'prompt': prompt}, f, indent=4)
        token_input_count += token_counter(model=config.param.base_llm, text=prompt[0]['content'])
        token_output_count += token_counter(model=config.param.base_llm, text=response)
        strength = response

        prompt = [
            {
                'role': 'user',
                'content': (
                    'Here is your profile:\n'
                    f'{bio_str}\n'
                    'Here is the paper:\n'
                    f'{paper_content}\n'
                    "Please write a review of the paper based on the introduction and authors' profiles. You should write a paragraph of approximately 200 words.\n"
                    'You should only write about the weaknesses of the paper. It should be 200 words long.\n'
                ),
            }
        ]
        response = model_prompting(
            config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
        )[0]
        token_input_count += token_counter(model=config.param.base_llm, text=prompt[0]['content'])
        token_output_count += token_counter(model=config.param.base_llm, text=response)
        weakness = response

        # score based on strength and weakness
        # A score between 1 to 10 to evaluate the overall quality of the submission to an academic journal. It should be one of 1, 2, ..., 10. 1 is the lowest score while 10 is the highest score.

        prompt = [
            {
                'role': 'user',
                'content': (
                    'Here is the strength of the paper:\n'
                    f'{strength}\n'
                    'Here is the weakness of the paper:\n'
                    f'{weakness}\n'
                    "Please rate the overall quality of the paper on a scale of 1 to 10. 1 is the lowest score while 10 is the highest score.\n"
                    "You should just provide one number as the score and nothing else.\n"
                    f"Your score is: "
                ),
            }
        ]
        response = model_prompting(
            config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
        )[0]
        token_input_count += token_counter(model=config.param.base_llm, text=prompt[0]['content'])
        token_output_count += token_counter(model=config.param.base_llm, text=response)
        score_raw = response       
    
        score_options = ['10', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        score = 0
        for score_option in score_options:
            if score_option in score_raw:
                score = int(score_option)

        strengths.append(strength)
        weaknesses.append(weakness)
        scores.append(int(score))

        print('token_input_count', token_input_count)
        print('token_output_count', token_output_count)
    
    token_input_count = 0
    token_output_count = 0
    
    # combine strengths, weaknesses, and scores
    prompt = [
        {
            'role': 'user',
            'content': (
                'Here are the strengths of the paper by different reviewers:\n'
                f'{strengths}\n'
                'Please summarize the strengths of the paper in a paragraph of approximately 200 words.\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    token_input_count += token_counter(model=config.param.base_llm, text=prompt[0]['content'])
    token_output_count += token_counter(model=config.param.base_llm, text=response)
    strength = response

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here are the weaknesses of the paper by different reviewers:\n'
                f'{weaknesses}\n'
                'Please summarize the weaknesses of the paper in a paragraph of approximately 200 words.\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    token_input_count += token_counter(model=config.param.base_llm, text=prompt[0]['content'])
    token_output_count += token_counter(model=config.param.base_llm, text=response)
    weakness = response

    print('token_input_count', token_input_count)
    print('token_output_count', token_output_count)

    return strength, weakness, scores


def write_review_with_only_citations(
    paper_content: str, ref_contents: List[str], config: Config
) -> Tuple[str, str, List[float]]:
    ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the paper:\n'
                f'{paper_content}\n'
                'Here are the references of the paper:\n'
                f'{ref_strs}\n'
                'Please write a review of the paper based on the introduction and references. You should write a paragraph of approximately 200 words.\n'
                'You should only write about the strengths of the paper. It should be 200 words long.\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    strength = response

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the paper:\n'
                f'{paper_content}\n'
                'Here are the references of the paper:\n'
                f'{ref_strs}\n'
                'Please write a review of the paper based on the introduction and references. You should write a paragraph of approximately 200 words.\n'
                'You should only write about the weaknesses of the paper. It should be 200 words long.\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    weakness = response

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the strength of the paper:\n'
                f'{strength}\n'
                'Here is the weakness of the paper:\n'
                f'{weakness}\n'
                "Please rate the overall quality of the paper on a scale of 1 to 10. 1 is the lowest score while 10 is the highest score.\n"
                "You should just provide one number as the score and nothing else.\n"
                f"Your score is: "
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num, temperature=config.param.temperature
    )[0]
    score_options = ['10', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    score = 0
    for score_option in score_options:
        if score_option in response:
            score = int(score_option)

    return strength, weakness, [score]

def write_review(
    mode: str,
    intro: str,
    profiles: List[Profile],
    profiles_reviewers: List[Profile],
    full_content: Dict[str, Any],
    ref_contents: List[str],
    config: Config,
) -> Union[Tuple[str, str, List[float]], Tuple[str, str, List[float], Dict[str, Dict[str, Any]]]]:
    paper_content = ''
    for idx, section in enumerate(full_content):
        paper_content += f'{idx + 1}:\n\n'
        section_text = full_content[section]
        paper_content += section_text + '\n\n'

    if mode == 'author_only':
        return write_review_with_only_profiles(paper_content, profiles_reviewers, config)
    elif mode == 'citation_only':
        return write_review_with_only_citations(paper_content, ref_contents, config)
    elif mode == 'zero_shot':
        return write_review_zero_shot(paper_content, config)
    elif mode == 'research_town':
        return write_review_research_town(paper_content, profiles_reviewers, ref_contents, config)
    else:
        raise ValueError(f'Invalid review writing mode: {mode}')
