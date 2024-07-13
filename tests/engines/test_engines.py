from research_town.configs import Config
from research_town.engines import BaseResearchEngine

from ..constants.data_constants import agent_profile_A, research_paper_submission_A
from ..constants.db_constants import (
    example_agent_db,
    example_env_db,
    example_paper_db,
    example_progress_db,
)


def test_engine_fine_proj_participants():
    example_agent_db.reset_role_avaialbility()
    engine = BaseResearchEngine(
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        env_db=example_env_db,
        config=Config(),
    )
    engine.set_proj_leader(agent_profile_A)
    proj_participants = engine.find_proj_participants(
        proj_leader=agent_profile_A,
        proj_participant_num=2,
    )
    assert len(proj_participants) == 2


def test_engine_find_proj_reviewers():
    example_agent_db.reset_role_avaialbility()
    engine = BaseResearchEngine(
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        env_db=example_env_db,
        config=Config(),
    )
    engine.set_proj_leader(agent_profile_A)
    reviewers = engine.find_reviewers(
        paper_submission=research_paper_submission_A,
        reviewer_num=2,
    )
    assert len(reviewers) == 2


def test_engine_find_chair():
    example_agent_db.reset_role_avaialbility()
    engine = BaseResearchEngine(
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        env_db=example_env_db,
        config=Config(),
    )
    engine.set_proj_leader(agent_profile_A)
    chair = engine.find_chair(
        paper_submission=research_paper_submission_A,
    )
    assert chair is not None
