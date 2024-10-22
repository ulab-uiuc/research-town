# common.py

import json
import os
from typing import Any, Dict, List, Optional, Union

SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/'


def save_benchmark(benchmark: Dict[str, Any], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark, f, indent=4, ensure_ascii=False)
    print(f'Benchmark saved to {output_path}')


def load_benchmark(input_path: str) -> Any:
    with open(input_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_cache_item(
    cache_path: Optional[str],
    paper_key: str,
    item_key: Union[str, List[Optional[str]], None],
) -> Optional[Union[str, List[str]]]:
    if not cache_path:
        return None

    try:
        with open(cache_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                cache = json.loads(line)
                if cache.get('paper_key', '') == paper_key:
                    value = cache.get(item_key)
                    if isinstance(value, (str, list, type(None))):
                        return value
                    return None
    except Exception as e:
        raise ValueError(f'Error loading cache for {paper_key}: {e}')
    return None


def write_cache_item(
    cache_path: Optional[str], paper_key: str, item_key: str, value: Any
) -> None:
    if not cache_path:
        return

    try:
        with open(cache_path, 'a', encoding='utf-8') as outfile:
            cache_entry = {'paper_key': paper_key, item_key: value}
            outfile.write(json.dumps(cache_entry) + '\n')
    except Exception as e:
        raise ValueError(f'Error writing cache for {paper_key}: {e}')
