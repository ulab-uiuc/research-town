from research_town.agents import AgentManager
from research_town.config import Config

from .db_constants import example_profile_db

example_agent_manager = AgentManager(config=Config(), profile_db=example_profile_db)
