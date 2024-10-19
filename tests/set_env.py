from tempfile import TemporaryDirectory
from typing import Generator

import pytest
from pytest import MonkeyPatch

from research_town.dbs.db_provider import DatabaseClientHandler


@pytest.fixture(autouse=True)
def set_env_variable(monkeypatch: MonkeyPatch) -> Generator[None, None, None]:
    """
    This fixture sets the DATABASE_FOLDER_PATH environment variable to a temporary directory path
    """
    import logging

    logging.error('set_env_variable')
    # Create a temporary directory
    temp_dir = TemporaryDirectory()

    # Set the environment variable to the temporary directory path
    monkeypatch.setenv('DATABASE_FOLDER_PATH', temp_dir.name)

    # Yield control to the tests
    yield

    # Cleanup the temporary directory after the session is over
    logging.error('cleanup')
    DatabaseClientHandler.reset_client_instance()
    temp_dir.cleanup()
