from beartype.typing import Any, Dict, List, Optional
from pydantic import BaseModel

from research_town.configs import AgentPromptTemplate, EvalPromptTemplate
from tests.constants.config_constants import example_config


def mock_papers(corpus: List[str], query: str, num: int) -> List[str]:
    return corpus[:num]


def mock_prompting(
    llm_model: str,
    prompt: List[Dict[str, str]],
    return_num: Optional[int] = 3,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    mode: Optional[str] = None,
) -> List[str]:
    agent_prompt_template = example_config.agent_prompt_template
    eval_prompt_template = example_config.eval_prompt_template
    if prompt[0]['content'] == agent_prompt_template.write_bio['sys_prompt']:
        return ['Bio1', 'Bio2', 'Bio3']
    elif prompt[0]['content'] == agent_prompt_template.review_literature['sys_prompt']:
        return ['Insight1', 'Insight2', 'Insight3']
    elif prompt[0]['content'] == agent_prompt_template.brainstorm_idea['sys_prompt']:
        return ['Idea1', 'Idea2', 'Idea3']
    elif prompt[0]['content'] == agent_prompt_template.discuss_idea['sys_prompt']:
        return ['Summarized idea1', 'Summarized idea2', 'Summarized idea3']
    elif prompt[0]['content'] == agent_prompt_template.write_proposal['sys_prompt']:
        return ['Paper abstract1', 'Paper abstract2', 'Paper abstract3']
    elif prompt[0]['content'] == agent_prompt_template.write_review_summary['sys_prompt']:
        return [
            'Summary of the paper1',
            'Summary of the paper2',
            'Summary of the paper3',
        ]
    elif prompt[0]['content'] == agent_prompt_template.write_review_strength['sys_prompt']:
        return [
            'Strength of the paper1',
            'Strength of the paper2',
            'Strength of the paper3',
        ]
    elif prompt[0]['content'] == agent_prompt_template.write_review_weakness['sys_prompt']:
        return [
            'Weakness of the paper1',
            'Weakness of the paper2',
            'Weakness of the paper3',
        ]
    elif prompt[0]['content'] == agent_prompt_template.write_review_score['sys_prompt']:
        return [
            'Based on the given information, I would give this submission a score of 8 out of 10.',
            'Based on the given information, I would give this submission a score of 6 out of 10.',
            'Based on the given information, I would give this submission a score of 5 out of 10.',
        ]
    elif (
        prompt[0]['content'] == agent_prompt_template.write_metareview_summary['sys_prompt']
    ):
        return ['Meta review summary1', 'Meta review summary2', 'Meta review summary3']
    elif (
        prompt[0]['content'] == agent_prompt_template.write_metareview_strength['sys_prompt']
    ):
        return [
            'Meta review strength1',
            'Meta review strength2',
            'Meta review strength3',
        ]
    elif (
        prompt[0]['content'] == agent_prompt_template.write_metareview_weakness['sys_prompt']
    ):
        return [
            'Meta review weakness1',
            'Meta review weakness2',
            'Meta review weakness3',
        ]
    elif (
        prompt[0]['content'] == agent_prompt_template.write_metareview_decision['sys_prompt']
    ):
        return ['accept', 'accept', 'reject']
    elif prompt[0]['content'] == agent_prompt_template.write_rebuttal['sys_prompt']:
        return ['Rebuttal text1', 'Rebuttal text2', 'Rebuttal text3']
    elif prompt[0]['content'] == eval_prompt_template.insight_quality['sys_prompt']:
        return ['Insight quality1', 'Insight quality2', 'Insight quality3']
    elif prompt[0]['content'] == eval_prompt_template.idea_quality['sys_prompt']:
        return ['Idea quality1', 'Idea quality2', 'Idea quality3']
    elif prompt[0]['content'] == eval_prompt_template.proposal_quality['sys_prompt']:
        return ['Paper quality1', 'Paper quality2', 'Paper quality3']
    elif prompt[0]['content'] == eval_prompt_template.review_quality['sys_prompt']:
        return ['Review quality1', 'Review quality2', 'Review quality3']
    elif prompt[0]['content'] == eval_prompt_template.rebuttal_quality['sys_prompt']:
        return ['Rebuttal quality1', 'Rebuttal quality2', 'Rebuttal quality3']
    elif prompt[0]['content'] == eval_prompt_template.metareview_quality['sys_prompt']:
        return ['Meta review quality1', 'Meta review quality2', 'Meta review quality3']

    return ['Default response1', 'Default response2', 'Default response3']


class MockModel(BaseModel):
    data: str


def mock_api_call_success(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    return ['Success']


def mock_api_call_failure(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    raise Exception('API call failed')
