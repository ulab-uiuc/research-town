from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.dbs import (
    EnvLogDB,
    PaperProfileDB,
    ProgressDB,
    ResearchMetaReviewForPaperSubmission,
    ResearchRebuttalForPaperSubmission,
    ResearchReviewForPaperSubmission,
)
from research_town.envs import PaperSubmissionMultiAgentEnv, PeerReviewMultiAgentEnv
from tests.constants.data_constants import (
    agent_profile_A,
    agent_profile_B,
    research_paper_submission_A,
)
from tests.mocks.mocking_func import mock_prompting


@patch('research_town.utils.agent_prompter.model_prompting')
def test_peer_review_env(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    env = PeerReviewMultiAgentEnv(
        paper_db=PaperProfileDB(),
        env_db=EnvLogDB(),
        progress_db=ProgressDB(),
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
    assert isinstance(env.reviews[0], ResearchReviewForPaperSubmission)

    assert isinstance(env.rebuttals, list)
    assert len(env.rebuttals) == 2
    assert isinstance(env.rebuttals[0], ResearchRebuttalForPaperSubmission)

    assert isinstance(env.meta_review, ResearchMetaReviewForPaperSubmission)
    assert isinstance(env.meta_review.decision, bool)


@patch('research_town.utils.agent_prompter.model_prompting')
def test_paper_submission_env(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting

    env = PaperSubmissionMultiAgentEnv(
        paper_db=PaperProfileDB(),
        env_db=EnvLogDB(),
        progress_db=ProgressDB(),
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
    assert env.paper.abstract is not None
    assert env.paper.abstract == 'Paper abstract1'
    assert exit_status is True
