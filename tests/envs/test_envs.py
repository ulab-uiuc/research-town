from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.dbs import AgentProfileDB, EnvLogDB, PaperProfileDB, ProgressDB
from research_town.envs import (
    PaperSubmissionMultiAgentEnvironment,
    PeerReviewMultiAgentEnv,
)
from tests.constants.db_constants import (
    agent_profile_A,
    agent_profile_B,
    paper_profile_A,
)
from tests.mocks.mocking_func import mock_papers


@patch('research_town.utils.agent_prompter.model_prompting')
def test_paper_rebuttal_env(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = ['Paper Rebuttal Environment.']
    agent_db = AgentProfileDB()
    paper_db = PaperProfileDB()
    env_db = EnvLogDB()
    progress_db = ProgressDB()
    config = Config()
    env = PeerReviewMultiAgentEnv(
        agent_profiles=[agent_profile_A, agent_profile_B, agent_profile_B],
        agent_roles=['proj_leader', 'reviewer', 'chair'],
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )

    submission = paper_profile_A
    env.initialize_submission(submission)

    env.run()

    assert isinstance(env.reviews, list)
    assert len(env.reviews) > 0
    assert isinstance(env.decision, str)
    assert env.decision in ['accept', 'reject', 'boarderline']
    assert isinstance(env.rebuttals, list)
    assert len(env.rebuttals) > 0


@patch('research_town.utils.agent_prompter.model_prompting')
@patch('research_town.utils.agent_prompter.get_related_papers')
def test_paper_submission_env(
    mock_get_related_papers: MagicMock,
    mock_model_prompting: MagicMock,
) -> None:
    mock_get_related_papers.side_effect = mock_papers
    mock_model_prompting.return_value = ['This is a paper.']
    agent_db = AgentProfileDB()
    paper_db = PaperProfileDB()
    env_db = EnvLogDB()
    progress_db = ProgressDB()
    config = Config()
    env = PaperSubmissionMultiAgentEnvironment(
        agent_profiles=[agent_profile_A],
        agent_roles=['proj_leader'],
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )
    env.run()
    assert env.paper.abstract is not None
    assert env.paper.abstract == 'This is a paper.'
