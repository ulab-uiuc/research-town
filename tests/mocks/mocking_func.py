from beartype.typing import Any, List, Optional
from pydantic import BaseModel


def mock_papers(corpus: List[str], query: str, num: int) -> List[str]:
    return corpus[:num]


def mock_prompting(
    llm_model: str,
    prompt: str,
    return_num: Optional[int] = 2,
    max_tokens: Optional[int] = 512,
) -> List[str]:
    if (
        'Please give some reviews based on the following inputs and external data.'
        in prompt
    ):
        return ['This is a paper review for MambaOut.']
    elif 'Please provide a score for the following reviews.' in prompt:
        return ['2']
    elif 'Please give me 3 to 5 novel ideas and insights' in prompt:
        return ['This is a research idea.']
    elif 'summarize the keywords' in prompt:
        return ['Graph Neural Network']
    elif 'Given a list of research ideas, please summarize them' in prompt:
        return ['This is a summarized idea.']
    return ['Default response']


class MockModel(BaseModel):
    data: str


def mock_api_call_success(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    return ['Success']


def mock_api_call_failure(*args: Any, **kwargs: Any) -> Optional[List[str]]:
    raise Exception('API call failed')
