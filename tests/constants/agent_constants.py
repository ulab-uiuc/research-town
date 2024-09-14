from research_town.agents import ResearchAgentManager
from .db_constants import example_profile_db
from research_town.config import Config

example_research_agent_manager = ResearchAgentManager(config=Config(), profile_db=example_profile_db)