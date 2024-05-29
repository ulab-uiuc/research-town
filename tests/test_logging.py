from research_town.agents.agent_base import BaseResearchAgent
from research_town.utils.logging import logging_callback
from tests.constants import agent_profile_A


def test_logging_callback() -> None:
    logging_callback()
    logging_callback([])
    logging_callback([{'text': 'text', 'level': 'INFO'}])
