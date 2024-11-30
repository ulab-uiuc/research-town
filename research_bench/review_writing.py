"""
Review Writing Process Evaluation
Input:   Real-world Papers
Process: Match Reviewers to Papers with Similar Interests
         Evaluate Reviewers' Reviews using Similarity Metrics
Output:  Reviewers' Similarity Scores
"""

from typing import List

from research_town.configs import Config
from research_town.data import Profile
from research_town.utils.model_prompting import model_prompting

# Baselines


def write_review_with_only_profiles(
    intro: str, profiles: List[Profile], config: Config
) -> str:
    bio_strs = '\n'.join([profile.bio for profile in profiles])

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here are the profiles of the authors:\n'
                f'{bio_strs}\n'
                'Here is the introduction of a paper:\n'
                f'{intro}\n'
                "Please write a proposal of the paper based on the introduction and authors' profiles. You should write a paragraph of approximately 200 words.\n"
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num
    )[0]
    return response


def write_review_with_only_citations(
    intro: str, ref_contents: List[str], config: Config
) -> str:
    ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the introduction of a paper:\n'
                f'{intro}\n'
                'Here are the references of the paper:\n'
                f'{ref_strs}\n'
                'Please write a review of the paper based on the introduction and references. You should write two paragraphs, each of approximately 200 words.\n'
                'First paragraph should start with Strength -\n'
                'Second paragraph should start with Weakness -\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num
    )[0]
    return response


def write_review_with_profiles_and_citations(
    intro: str, profiles: List[Profile], ref_contents: List[str], config: Config
) -> str:
    bio_strs = '\n'.join([profile.bio for profile in profiles])
    ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here are the profiles of the authors:\n'
                f'{bio_strs}\n'
                'Here is the introduction of a paper:\n'
                f'{intro}\n'
                'Here are the references of the paper:\n'
                f'{ref_strs}\n'
                "Please write a review of the paper based on the introduction, references, and authors' profiles. You should write two paragraphs, each of approximately 200 words.\n"
                'First paragraph should start with Strength -\n'
                'Second paragraph should start with Weakness -\n'
            ),
        }
    ]
    response = model_prompting(
        config.param.base_llm, prompt, max_token_num=config.param.max_token_num
    )[0]
    return response


def write_review(
    mode: str,
    intro: str,
    profiles: List[Profile],
    ref_contents: List[str],
    config: Config,
) -> str:
    if mode == 'only_profiles':
        return write_review_with_only_profiles(intro, profiles, config)
    elif mode == 'only_citations':
        return write_review_with_only_citations(intro, ref_contents, config)
    elif mode == 'profiles_and_citations':
        return write_review_with_profiles_and_citations(
            intro, profiles, ref_contents, config
        )
    else:
        raise ValueError(f'Invalid review writing mode: {mode}')
