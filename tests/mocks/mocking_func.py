from beartype.typing import Any, Dict, List, Optional
from pydantic import BaseModel

from research_town.configs import AgentPromptTemplateConfig, EvalPromptTemplateConfig


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
    agent_template_config = AgentPromptTemplateConfig()
    eval_template_config = EvalPromptTemplateConfig()
    if prompt[0]['content'] == agent_template_config.write_bio['intro']:
        return ['Bio1', 'Bio2', 'Bio3']
    elif prompt[0]['content'] == agent_template_config.review_literature['intro']:
        return ['Insight1', 'Insight2', 'Insight3']
    elif prompt[0]['content'] == agent_template_config.brainstorm_idea['intro']:
        return ['Idea1', 'Idea2', 'Idea3']
    elif prompt[0]['content'] == agent_template_config.discuss_idea['intro']:
        return ['Summarized idea1', 'Summarized idea2', 'Summarized idea3']
    elif prompt[0]['content'] == agent_template_config.write_proposal['intro']:
        return ['Paper abstract1', 'Paper abstract2', 'Paper abstract3']
    elif prompt[0]['content'] == agent_template_config.write_review_summary['intro']:
        return [
            'Summary of the paper1',
            'Summary of the paper2',
            'Summary of the paper3',
        ]
    elif prompt[0]['content'] == agent_template_config.write_review_strength['intro']:
        return [
            'Strength of the paper1',
            'Strength of the paper2',
            'Strength of the paper3',
        ]
    elif prompt[0]['content'] == agent_template_config.write_review_weakness['intro']:
        return [
            'Weakness of the paper1',
            'Weakness of the paper2',
            'Weakness of the paper3',
        ]
    elif prompt[0]['content'] == agent_template_config.write_review_score['intro']:
        return [
            'Based on the given information, I would give this submission a score of 8 out of 10.',
            'Based on the given information, I would give this submission a score of 6 out of 10.',
            'Based on the given information, I would give this submission a score of 5 out of 10.',
        ]
    elif (
        prompt[0]['content'] == agent_template_config.write_metareview_summary['intro']
    ):
        return ['Meta review summary1', 'Meta review summary2', 'Meta review summary3']
    elif (
        prompt[0]['content'] == agent_template_config.write_metareview_strength['intro']
    ):
        return [
            'Meta review strength1',
            'Meta review strength2',
            'Meta review strength3',
        ]
    elif (
        prompt[0]['content'] == agent_template_config.write_metareview_weakness['intro']
    ):
        return [
            'Meta review weakness1',
            'Meta review weakness2',
            'Meta review weakness3',
        ]
    elif (
        prompt[0]['content'] == agent_template_config.write_metareview_decision['intro']
    ):
        return ['accept', 'accept', 'reject']
    elif prompt[0]['content'] == agent_template_config.write_rebuttal['intro']:
        return ['Rebuttal text1', 'Rebuttal text2', 'Rebuttal text3']
    elif prompt[0]['content'] == agent_template_config.discuss['intro']:
        return [
            'Continued conversation1',
            'Continued conversation2',
            'Continued conversation3',
        ]
    elif prompt[0]['content'] == eval_template_config.insight_quality['intro']:
        return ['Insight quality1', 'Insight quality2', 'Insight quality3']
    elif prompt[0]['content'] == eval_template_config.idea_quality['intro']:
        return ['Idea quality1', 'Idea quality2', 'Idea quality3']
    elif prompt[0]['content'] == eval_template_config.paper_quality['intro']:
        return ['Paper quality1', 'Paper quality2', 'Paper quality3']
    elif prompt[0]['content'] == eval_template_config.review_quality['intro']:
        return ['Review quality1', 'Review quality2', 'Review quality3']
    elif prompt[0]['content'] == eval_template_config.rebuttal_quality['intro']:
        return ['Rebuttal quality1', 'Rebuttal quality2', 'Rebuttal quality3']
    elif prompt[0]['content'] == eval_template_config.metareview_quality['intro']:
        return ['Meta review quality1', 'Meta review quality2', 'Meta review quality3']

    return ['Default response1', 'Default response2', 'Default response3']


class MockModel(BaseModel):
    data: str


def mock_api_call_success(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    return ['Success']


def mock_api_call_failure(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    raise Exception('API call failed')
