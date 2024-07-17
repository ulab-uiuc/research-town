from beartype.typing import Any, List, Optional
from pydantic import BaseModel

from research_town.configs import PromptTemplateConfig


def mock_papers(corpus: List[str], query: str, num: int) -> List[str]:
    return corpus[:num]


def mock_prompting(
    llm_model: str,
    prompt: str,
    return_num: Optional[int] = 3,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    mode: Optional[str] = None,
) -> List[str]:
    template_config = PromptTemplateConfig()

    # Check which template the prompt matches
    if prompt.startswith(template_config.write_bio.split('{')[0]):
        return ['Bio1', 'Bio2', 'Bio3']
    if prompt.startswith(template_config.find_collaborators.split('{')[0]):
        return ['Collaborator1', 'Collaborator2', 'Collaborator3']
    elif prompt.startswith(template_config.review_literature.split('{')[0]):
        return ['Insight1', 'Insight2', 'Insight3']
    elif prompt.startswith(template_config.brainstorm_idea.split('{')[0]):
        return ['Idea1', 'Idea2', 'Idea3']
    elif prompt.startswith(template_config.discuss_idea.split('{')[0]):
        return ['Summarized idea1', 'Summarized idea2', 'Summarized idea3']
    elif prompt.startswith(template_config.write_paper.split('{')[0]):
        return ['Paper abstract1', 'Paper abstract2', 'Paper abstract3']
    elif prompt.startswith(template_config.write_review_summary.split('{')[0]):
        return [
            'Summary of the paper1',
            'Summary of the paper2',
            'Summary of the paper3',
        ]
    elif prompt.startswith(template_config.write_review_strength.split('{')[0]):
        return [
            'Strength of the paper1',
            'Strength of the paper2',
            'Strength of the paper3',
        ]
    elif prompt.startswith(template_config.write_review_weakness.split('{')[0]):
        return [
            'Weakness of the paper1',
            'Weakness of the paper2',
            'Weakness of the paper3',
        ]
    elif prompt.startswith(template_config.write_review_score.split('{')[0]):
        return ['8', '7', '6']
    elif prompt.startswith(template_config.write_meta_review_summary.split('{')[0]):
        return ['Meta review summary1', 'Meta review summary2', 'Meta review summary3']
    elif prompt.startswith(template_config.write_meta_review_strength.split('{')[0]):
        return [
            'Meta review strength1',
            'Meta review strength2',
            'Meta review strength3',
        ]
    elif prompt.startswith(template_config.write_meta_review_weakness.split('{')[0]):
        return [
            'Meta review weakness1',
            'Meta review weakness2',
            'Meta review weakness3',
        ]
    elif prompt.startswith(template_config.write_meta_review_decision.split('{')[0]):
        return ['accept', 'accept', 'reject']
    elif prompt.startswith(template_config.write_rebuttal.split('{')[0]):
        return ['Rebuttal text1', 'Rebuttal text2', 'Rebuttal text3']
    elif prompt.startswith(template_config.discuss.split('{')[0]):
        return [
            'Continued conversation1',
            'Continued conversation2',
            'Continued conversation3',
        ]
    return ['Default response1', 'Default response2', 'Default response3']


class MockModel(BaseModel):
    data: str


def mock_api_call_success(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    return ['Success']


def mock_api_call_failure(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    raise Exception('API call failed')
