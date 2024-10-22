# common.py

import json
import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/'


def save_benchmark(benchmark: Dict[str, Any], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark, f, indent=4, ensure_ascii=False)
    print(f'Benchmark saved to {output_path}')


def load_benchmark(input_path: str) -> Any:
    with open(input_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def with_cache(
    cache_dir: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(arxiv_id: str, *args: Any, **kwargs: Any) -> Any:
            if not cache_dir:
                return func(arxiv_id, *args, **kwargs)

            cache_path = Path(cache_dir) / f'{arxiv_id}_{func.__name__}.json'
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            if cache_path.exists():
                with cache_path.open('r') as f:
                    return json.load(f)

            result = func(arxiv_id, *args, **kwargs)
            with cache_path.open('w') as f:
                json.dump(result, f)

            return result

        return wrapper

    return decorator
