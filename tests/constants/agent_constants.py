from research_town.agents import AgentManager
from .db_constants import example_profile_db
from .config_constants import example_config

example_agent_manager = AgentManager(config=example_config, profile_db=example_profile_db)
