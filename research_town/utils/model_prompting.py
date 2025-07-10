import os

import litellm
from beartype import beartype
from beartype.typing import Dict, List, Optional

from .error_handler import api_calling_error_exponential_backoff


@beartype
@api_calling_error_exponential_backoff(retries=5, base_wait_time=1)
def model_prompting(
    llm_model: str,
    messages: List[Dict[str, str]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    mode: Optional[str] = None,
) -> List[str]:
    """
    Select model via router in LiteLLM.
    """
    # if Qwen, trim messages using litellm's message trimming function
    from litellm.utils import trim_messages

    if llm_model.startswith('Qwen'):
        messages = trim_messages(
            messages=messages,
            model='Qwen/Qwen2.5-7B-Instruct',
            max_tokens=30000,  # Qwen's max context length is 32k tokens
        )
        # if single message exceeds max_tokens, trim it down to max_tokens
        # for message in messages:
        #     if 'content' in message:
        #         tokenized_length = litellm.token_counter(model=llm_model, messages=messages)
        #         import pdb; pdb.set_trace()
        #         if tokenized_length > 32768:
        #             # Trim the content to fit within the max_tokens limit
        #             tokenized = litellm.utils.tokenize(message['content'])
        #             # Trimming the tokenized content to max_tokens
        #             trimmed_content = litellm.utils.detokenize(tokenized[:32768])
        #             message['content'] = trimmed_content
    if llm_model.startswith('deepseek-ai') or llm_model.startswith('Qwen'):
        completion = litellm.completion(
            model='openai/' + llm_model,
            messages=messages,
            max_tokens=max_token_num,
            # for some models, 'n'(The number of chat completion choices ) is not supported.
            n=return_num,
            top_p=top_p,
            temperature=temperature,
            stream=stream,
            base_url='https://api.together.xyz/v1',
            api_key=os.environ.get('TOGETHER_API_KEY'),
        )

    else:
        completion = litellm.completion(
            model=llm_model,
            messages=messages,
            max_tokens=max_token_num,
            # for some models, 'n'(The number of chat completion choices ) is not supported.
            n=return_num,
            top_p=top_p,
            temperature=temperature,
            stream=stream,
        )
    content = completion.choices[0].message.content
    content_l = [content]
    return content_l
