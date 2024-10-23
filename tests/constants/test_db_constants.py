import pytest

from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB

from .config_constants import example_config
from .data_constants import (
    agent_paper_metareview_log,
    agent_paper_rebuttal_log,
    agent_paper_review_log,
    paper_A,
    paper_B,
    paper_C,
    profile_A,
    profile_B,
    profile_C,
    research_idea_A,
    research_idea_B,
    research_insight_A,
    research_insight_B,
    research_proposal_A,
    research_proposal_B,
)


# Fixture for ProfileDB, dependent on the set_env_variable
@pytest.fixture
def example_profile_db(set_env_variable: None) -> ProfileDB:
    """
    This fixture creates an instance of ProfileDB with the example profiles
    """
    profile_db = ProfileDB(config=example_config.database)
    profile_db.add(profile_A)
    profile_db.add(profile_B)
    profile_db.add(profile_C)
    return profile_db


@pytest.fixture
def example_paper_db(set_env_variable: None) -> PaperDB:
    """
    This fixture creates an instance of PaperDB with the example papers
    """
    paper_db = PaperDB(config=example_config.database)
    paper_db.add(paper_A)
    paper_db.add(paper_B)
    paper_db.add(paper_C)
    return paper_db


@pytest.fixture
def example_progress_db(set_env_variable: None) -> ProgressDB:
    """
    This fixture creates an instance of ProgressDB with the example research ideas, insights, and proposals
    """
    progress_db = ProgressDB(config=example_config.database)
    progress_db.add(research_idea_A)
    progress_db.add(research_idea_B)
    progress_db.add(research_insight_A)
    progress_db.add(research_insight_B)
    progress_db.add(research_proposal_A)
    progress_db.add(research_proposal_B)
    return progress_db


@pytest.fixture
def example_log_db(set_env_variable: None) -> LogDB:
    """
    This fixture creates an instance of LogDB with the example logs"""
    log_db = LogDB(config=example_config.database)
    log_db.add(agent_paper_review_log)
    log_db.add(agent_paper_rebuttal_log)
    log_db.add(agent_paper_metareview_log)
    return log_db
