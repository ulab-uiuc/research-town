import time

from research_town.utils.error_handler import (
    api_calling_error_exponential_backoff,
    parsing_error_exponential_backoff,
)
from tests.mocks.mocking_func import (
    MockModel,
    mock_api_call_failure,
    mock_api_call_success,
)


class MockClass:
    @parsing_error_exponential_backoff()
    def mock_parsing_call_success(self) -> MockModel:
        return MockModel(data='Success')

    @parsing_error_exponential_backoff(retries=3, base_wait_time=1)
    def mock_parsing_call_failure(self) -> MockModel:
        raise Exception('Parsing call failed')


def test_api_calling_error_exponential_backoff_success() -> None:
    decorated_func = api_calling_error_exponential_backoff()(mock_api_call_success)
    result = decorated_func()
    assert result == ['Success']


def test_api_calling_error_exponential_backoff_failure() -> None:
    decorated_func = api_calling_error_exponential_backoff(retries=3, base_wait_time=1)(
        mock_api_call_failure
    )
    start_time = time.time()
    result = decorated_func()
    end_time = time.time()
    assert result is None
    assert (
        3 <= end_time - start_time < 15
    )  # Considering 1 + 2 + 4 + 8 seconds of wait time


def test_parsing_error_exponential_backoff_success() -> None:
    mock_instance = MockClass()
    result = mock_instance.mock_parsing_call_success()
    assert result == MockModel(data='Success')


def test_parsing_error_exponential_backoff_failure() -> None:
    mock_instance = MockClass()
    start_time = time.time()
    result = mock_instance.mock_parsing_call_failure()
    end_time = time.time()
    assert result is None
    assert (
        3 <= end_time - start_time < 15
    )  # Considering 1 + 2 + 4 + 8 seconds of wait time
