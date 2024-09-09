from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.dbs import MetaReview, Rebuttal, Review
from research_town.envs import ProposalWritingEnv, ReviewWritingEnv
from tests.constants.data_constants import (
    agent_profile_A,
    agent_profile_B,
    research_paper_submission_A,
)
from tests.constants.db_constants import (
    example_env_db,
    example_paper_db,
    example_progress_db,
)
from tests.mocks.mocking_func import mock_prompting


@patch('research_town.utils.agent_prompter.model_prompting')
def test_peer_review_env(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    env = ReviewWritingEnv(
        env_db=example_env_db,
        progress_db=example_progress_db,
        paper_db=example_paper_db,
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
        agent_roles=['proj_leader', 'reviewer', 'reviewer', 'chair'],
        agent_models=[
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        ],
        paper=research_paper_submission_A,
    )
    env.run()
    exit_status = env.on_exit()

    assert exit_status is True

    assert isinstance(env.reviews, list)
    assert len(env.reviews) == 2
    assert isinstance(env.reviews[0], Review)


@patch('research_town.utils.agent_prompter.model_prompting')
def test_paper_submission_env(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting

    env = ProposalWritingEnv(
        env_db=example_env_db,
        progress_db=example_progress_db,
        paper_db=example_paper_db,
        config=Config(),
    )
    env.on_enter(
        time_step=0,
        stop_flag=False,
        agent_profiles=[agent_profile_A],
        agent_roles=['proj_leader'],
        agent_models=['together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'],
    )
    env.run()
    exit_status = env.on_exit()
    assert env.proposal.abstract is not None
    assert env.proposal.abstract == 'Paper abstract1'
    assert exit_status is True
