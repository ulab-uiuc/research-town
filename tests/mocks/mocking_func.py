from beartype.typing import Any, List, Optional
from pydantic import BaseModel

from research_town.configs import PromptTemplateConfig


def mock_papers(corpus: List[str], query: str, num: int) -> List[str]:
    return corpus[:num]


def mock_prompting(
    llm_model: str,
    prompt: str,
    return_num: Optional[int] = 2,
    max_tokens: Optional[int] = 512,
) -> List[str]:
    template_config = PromptTemplateConfig()

    # Check which template the prompt matches
    if prompt.startswith(template_config.find_collaborators.split('{')[0]):
        return ['Collaborator 1', 'Collaborator 2', 'Collaborator 3']
    elif prompt.startswith(template_config.query_paper.split('{')[0]):
        return ['Keyword 1', 'Keyword 2']
    elif prompt.startswith(template_config.review_literature.split('{')[0]):
        return ['Insight 1', 'Insight 2']
    elif prompt.startswith(template_config.brainstorm_idea.split('{')[0]):
        return ['Idea 1', 'Idea 2', 'Idea 3']
    elif prompt.startswith(template_config.discuss_idea.split('{')[0]):
        return ['Summarized idea 1', 'Summarized idea 2']
    elif prompt.startswith(template_config.write_paper.split('{')[0]):
        return ['Paper abstract']
    elif prompt.startswith(template_config.write_review_summary.split('{')[0]):
        return ['Summary of the paper']
    elif prompt.startswith(template_config.write_review_strength.split('{')[0]):
        return ['Strength of the paper']
    elif prompt.startswith(template_config.write_review_weakness.split('{')[0]):
        return ['Weakness of the paper']
    elif prompt.startswith(template_config.write_review_score.split('{')[0]):
        return ['8']
    elif prompt.startswith(template_config.write_meta_review_summary.split('{')[0]):
        return ['Meta review summary']
    elif prompt.startswith(template_config.write_meta_review_strength.split('{')[0]):
        return ['Meta review strength']
    elif prompt.startswith(template_config.write_meta_review_weakness.split('{')[0]):
        return ['Meta review weakness']
    elif prompt.startswith(template_config.write_meta_review_decision.split('{')[0]):
        return ['accept']
    elif prompt.startswith(template_config.write_rebuttal.split('{')[0]):
        return ['Rebuttal text']
    elif prompt.startswith(template_config.discuss.split('{')[0]):
        return ['Continued conversation']
    return ['Default response']


class MockModel(BaseModel):
    data: str


def mock_api_call_success(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    return ['Success']


def mock_api_call_failure(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    raise Exception('API call failed')
