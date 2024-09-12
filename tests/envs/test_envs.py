from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.dbs import Review
from research_town.envs import ProposalWritingEnv, ReviewWritingEnv
from tests.constants.data_constants import (
    agent_profile_A,
    agent_profile_B,
    research_proposal_A,
)
from tests.constants.db_constants import (
    example_agent_db,
    example_log_db,
    example_paper_db,
    example_progress_db,
)
from tests.mocks.mocking_func import mock_prompting


@patch('research_town.utils.agent_prompter.model_prompting')
def test_peer_review_env(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    env = ReviewWritingEnv(
        name='review_writing',
        log_db=example_log_db,
        progress_db=example_progress_db,
        paper_db=example_paper_db,
        agent_db=example_agent_db,
        config=Config(),
    )

    env.on_enter(
        time_step=0,
        stop_flag=False,
        agent_profiles=[
            agent_profile_A,
            agent_profile_B,
            agent_profile_B,
            agent_profile_A,
        ],
        agent_roles=['leader', 'reviewer', 'reviewer', 'chair'],
        agent_models=[
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        ],
        paper=research_proposal_A,
    )
    env.run()
    exit_status = env.on_exit()

    assert exit_status == 'proposal_accept'

    assert isinstance(env.reviews, list)
    assert len(env.reviews) == 2
    assert isinstance(env.reviews[0], Review)


@patch('research_town.utils.agent_prompter.model_prompting')
def test_proposal_env(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting

    env = ProposalWritingEnv(
<<<<<<< HEAD
        name='proposal_writing',
        log_db=example_log_db,
||||||| c45f97c
        env_db=example_env_db,
=======
        name='proposal_writing',
        env_db=example_env_db,
>>>>>>> 763c267652678b3f2a6f7a4e96382e61743ff1b0
        progress_db=example_progress_db,
        paper_db=example_paper_db,
        agent_db=example_agent_db,
        config=Config(),
    )
    env.on_enter(
        time_step=0,
        stop_flag=False,
        agent_profiles=[agent_profile_A],
        agent_roles=['leader'],
        agent_models=['together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'],
    )
    env.run()
    exit_status = env.on_exit()
    assert env.proposal.abstract is not None
    assert env.proposal.abstract == 'Paper abstract1'
    assert exit_status == 'start_review'
