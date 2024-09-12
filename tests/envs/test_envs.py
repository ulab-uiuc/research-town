from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.dbs import Review
from research_town.envs import ProposalWritingEnv, ReviewWritingEnv
from tests.constants.data_constants import agent_profile_A, research_proposal_A
from tests.constants.db_constants import (
    example_log_db,
    example_paper_db,
    example_profile_db,
    example_progress_db,
)
from tests.mocks.mocking_func import mock_prompting


@patch('research_town.utils.agent_prompter.model_prompting')
def test_review_writing_env(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    example_profile_db.reset_role_avaialbility()
    env = ReviewWritingEnv(
        name='review_writing',
        log_db=example_log_db,
        progress_db=example_progress_db,
        paper_db=example_paper_db,
        profile_db=example_profile_db,
        config=Config(),
    )

    env.on_enter(
        time_step=0,
        proposal=research_proposal_A,
        leader_profile=agent_profile_A,
    )
    env.run()
    exit_status = env.on_exit()

    assert exit_status == 'proposal_accept'

    assert isinstance(env.reviews, list)
    assert len(env.reviews) == 1
    assert isinstance(env.reviews[0], Review)


@patch('research_town.utils.agent_prompter.model_prompting')
def test_proposal_writing_env(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting

    example_profile_db.reset_role_avaialbility()
    env = ProposalWritingEnv(
        name='proposal_writing',
        log_db=example_log_db,
        progress_db=example_progress_db,
        paper_db=example_paper_db,
        profile_db=example_profile_db,
        config=Config(),
    )
    env.on_enter(
        time_step=0,
        leader_profile=agent_profile_A,
    )
    env.run()
    exit_status = env.on_exit()
    assert env.proposal.abstract is not None
    assert env.proposal.abstract == 'Paper abstract1'
    assert exit_status == 'start_review'
