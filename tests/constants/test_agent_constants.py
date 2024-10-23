import pytest

from research_town.agents import AgentManager
from research_town.dbs import ProfileDB

from .config_constants import example_config


@pytest.fixture
def example_agent_manager(example_profile_db: ProfileDB) -> AgentManager:
    return AgentManager(config=example_config, profile_db=example_profile_db)
