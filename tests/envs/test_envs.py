from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.dbs import (
    AgentProfileDB,
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
        agent_profiles=[
            agent_profile_A,
            agent_profile_B,
            agent_profile_B,
            agent_profile_A,
        ],
        agent_roles=['proj_leader', 'reviewer', 'reviewer', 'chair'],
        agent_db=AgentProfileDB(),
        paper_db=PaperProfileDB(),
        env_db=EnvLogDB(),
        progress_db=ProgressDB(),
        config=Config(),
    )

    meta_review, rebuttals, reviews = env.run(research_paper_submission_A)

    assert isinstance(reviews, list)
    assert len(reviews) == 2
    assert isinstance(reviews[0], ResearchReviewForPaperSubmission)

    assert isinstance(rebuttals, list)
    assert len(rebuttals) == 2
    assert isinstance(rebuttals[0], ResearchRebuttalForPaperSubmission)

    assert isinstance(meta_review, ResearchMetaReviewForPaperSubmission)
    assert isinstance(meta_review.decision, bool)


@patch('research_town.utils.agent_prompter.model_prompting')
def test_paper_submission_env(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting

    env = PaperSubmissionMultiAgentEnv(
        agent_profiles=[agent_profile_A],
        agent_roles=['proj_leader'],
        agent_db=AgentProfileDB(),
        paper_db=PaperProfileDB(),
        env_db=EnvLogDB(),
        progress_db=ProgressDB(),
        config=Config(),
    )
    paper = env.run()
    assert paper.abstract is not None
    assert paper.abstract == 'Paper abstract1'
