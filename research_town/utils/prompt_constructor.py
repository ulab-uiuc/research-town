import json
import os
from typing import Any, Dict, List, Union


def openai_format_prompt_construct(
    template: Dict[str, Union[str, List[str]]], input_data: Dict[str, Any]
) -> List[Dict[str, str]]:
    messages = []
    if 'sys_prompt' in template:
        sys_prompt = template['sys_prompt']
        assert isinstance(sys_prompt, str)
        messages.append({'role': 'system', 'content': sys_prompt})

    if 'fewshot_examples' in template:
        examples = template['fewshot_examples']
        assert len(examples) % 2 == 0
        for i, example in enumerate(examples):
            if i % 2 == 0:
                messages.append({'role': 'user', 'content': example})
            else:
                messages.append({'role': 'assistant', 'content': example})

    assert isinstance(template['template'], str)
    query = template['template'].format(**input_data)
    assert isinstance(query, str)
    messages.append({'role': 'user', 'content': query})

    return messages


def save_prompt_to_json(
    template_name: str, messages: List[Dict[str, Union[str, List[str]]]]
) -> None:
    file_name = f'{template_name}.log'
    directory_path = os.path.join('..', 'data', 'prompt_data')
    file_path = os.path.join(directory_path, file_name)

    with open(file_path, 'w') as log_file:
        json.dump(messages, log_file, indent=4)
