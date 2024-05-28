import math
import time
from functools import wraps
from typing import Type, Any, Callable, List, Optional, TypeVar, Union
from pydantic import BaseModel

INF = float(math.inf)

T = TypeVar('T', bound=Callable[..., Union[List[str], None]])

def exponential_backoff(
    retries: int = 5, base_wait_time: int = 1
) -> Callable[[T], T]:
    """
    Decorator for applying exponential backoff to a function.
    :param retries: Maximum number of retries.
    :param base_wait_time: Base wait time in seconds for the exponential backoff.
    """

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[List[str]]:
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    wait_time = base_wait_time * (2 ** attempts)
                    print(f"Attempt {attempts + 1} failed: {e}")
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    attempts += 1
            print(
                f"Failed to execute '{func.__name__}' after {retries} retries."
            )
            return None

        return wrapper  # type: ignore

    return decorator


def retry_eval(output_format: Type[BaseModel], retries: int = 5, base_wait_time: int = 1) -> Callable[..., BaseModel]:
    """
    Decorator to apply retry mechanism to a function with expected output format BaseModel.
    """

    def decorator(func: Callable[..., BaseModel]) -> Callable[..., BaseModel]:
        def wrapper(*args: Any, **kwargs: Any) -> BaseModel:
            attempts = 0
            while attempts < retries:
                try:
                    result = func(*args, **kwargs)
                    assert isinstance(result, output_format), f"Output format error: {result}"
                    return result
                except Exception as e:
                    wait_time = base_wait_time * (2 ** attempts)
                    print(f"Attempt {attempts + 1} failed: {e}")
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    attempts += 1
            print(f"Failed to execute '{func.__name__}' after {retries} retries.")
            return output_format()

        return wrapper

    return decorator