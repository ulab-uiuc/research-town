from typing import List, Optional

import litellm

from .decorator import exponential_backoff


@exponential_backoff(retries=5, base_wait_time=1)
def model_prompting(
    llm_model: str,
    prompt: str,
    return_num: Optional[int] = 2,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    """
    Select model via router in LiteLLM.
    """
    completion = litellm.completion(
    model=llm_model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=max_token_num,
    n=return_num, # for some models, 'n'(The number of chat completion choices ) is not supported.
    top_p=top_p,
    temperature=temperature,
    stream=stream,
)
    content = completion.choices[0].message.content
    content_l = [content]
    return content_l
