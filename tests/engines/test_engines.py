from research_town.configs import Config
from research_town.engines import BaseEngine

from ..constants.data_constants import agent_profile_A, research_paper_submission_A
from ..constants.db_constants import (
    example_agent_db,
    example_env_db,
    example_paper_db,
    example_progress_db,
)


def test_engine_fine_members() -> None:
    example_agent_db.reset_role_avaialbility()
    engine = BaseEngine(
        project_name='test',
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        env_db=example_env_db,
        config=Config(),
    )
    example_agent_db.set_leader(agent_profile_A)
    members = example_agent_db.invite_members(
        leader=agent_profile_A,
        member_num=2,
    )
    assert len(members) == 2


def test_engine_find_proj_reviewers() -> None:
    example_agent_db.reset_role_avaialbility()
    engine = BaseEngine(
        project_name='test',
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        env_db=example_env_db,
        config=Config(),
    )
    example_agent_db.set_leader(agent_profile_A)
    reviewers = example_agent_db.invite_reviewers(
        paper_submission=research_paper_submission_A,
        reviewer_num=2,
    )
    assert len(reviewers) == 2


def test_engine_invite_chair() -> None:
    example_agent_db.reset_role_avaialbility()
    engine = BaseEngine(
        project_name='test',
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        env_db=example_env_db,
        config=Config(),
    )
    example_agent_db.set_leader(agent_profile_A)
    chair = example_agent_db.invite_chairs(
        paper_submission=research_paper_submission_A,
        chair_num=1,
    )[0]
    assert chair is not None
