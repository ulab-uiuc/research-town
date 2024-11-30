"""
Review Writing Process Evaluation
Input:   Real-world Papers
Process: Match Reviewers to Papers with Similar Interests
         Evaluate Reviewers' Reviews using Similarity Metrics
Output:  Reviewers' Similarity Scores
"""

from typing import List

from research_town.agents import AgentManager
from research_town.configs import Config
from research_town.data import Profile
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.envs import ReviewWritingEnv
from research_town.utils.model_prompting import model_prompting

# Baseline
def write_proposal_with_only_citations(intro: str, ref_contents: List[str], config: Config) -> str:
    ref_strs = '\n'.join([ref for ref in ref_contents if ref is not None])

    prompt = [
        {
            'role': 'user',
            'content': (
                'Here is the introduction of a paper:\n'
                f'{intro}\n'
                'Here are the references of the paper:\n'
                f'{ref_strs}\n'
                'Please write a proposal based on the introduction and references. You should write two paragraphs, each of approximately 200 words.\n'
                'First paragraph should start with Strength -\n'
                'Second paragraph should start with Weakness -\n'
            ),
        }
    ]
    response = model_prompting(config.param.base_llm, prompt, max_token_num=config.param.max_token_num)[0]
    return response

