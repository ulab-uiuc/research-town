from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.envs import ProposalWritingEnv, ReviewWritingEnv
from tests.constants.agent_constants import example_agent_manager
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
        config=Config(),
        agent_manager=example_agent_manager,
    )
    leader = example_agent_manager.create_leader(agent_profile_A)
    env.on_enter(
        proposal=research_proposal_A,
        leader=leader,
    )
    run_result = env.run()
    if run_result is not None:
        for progress, agent in run_result:
            pass
    exit_status, exit_dict = env.on_exit()

    assert exit_status == 'proposal_accept'
    assert exit_dict['metareview'] is not None


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
        config=Config(),
        agent_manager=example_agent_manager,
    )
    leader = example_agent_manager.create_leader(agent_profile_A)
    env.on_enter(
        leader=leader,
    )
    run_result = env.run()
    if run_result is not None:
        for progress, agent in run_result:
            pass
    exit_status, exit_dict = env.on_exit()
    proposal = exit_dict['proposal']
    for p in proposal:
        assert p.content == 'Paper abstract1'
    assert exit_status == 'start_review'
