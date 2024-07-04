from unittest.mock import MagicMock, patch

from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfileDB,
    ProgressDB,
)
from research_town.envs import (
    PaperSubmissionMultiAgentEnvironment,
    PeerReviewMultiAgentEnv,
)
from tests.mocks.mocking_func import mock_papers, mock_prompting

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


@patch('research_town.utils.agent_prompter.model_prompting')
@patch('research_town.utils.agent_prompter.get_related_papers')
def test_dummy_research_town(
    mock_get_related_papers: MagicMock,
    mock_model_prompting: MagicMock,
) -> None:
    mock_get_related_papers.side_effect = mock_papers
    mock_model_prompting.side_effect = mock_prompting

    agent_list: List[str] = ['Jiaxuan You', 'Jure Leskovec', 'Geoffrey Hinton']
    role_list: List[Role] = ['proj_leader', 'reviewer', 'chair']

    # Create Environment and Agents
    agent_profiles = [
        AgentProfile(name=agent, bio='A researcher in machine learning.')
        for agent in agent_list
    ]
    agent_db = AgentProfileDB()
    paper_db = PaperProfileDB()
    env_db = EnvLogDB()
    progress_db = ProgressDB()
    config = Config()
    paper_submission_env = PaperSubmissionMultiAgentEnvironment(
        agent_profiles=agent_profiles,
        agent_roles=role_list,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )
    peer_review_env = PeerReviewMultiAgentEnv(
        agent_profiles=agent_profiles,
        agent_roles=role_list,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )

    # Paper Submission
    submission_done = False
    while not submission_done:
        paper_submission_env.step()
        submission_done = paper_submission_env.terminated
    paper = paper_submission_env.paper

    # Peer Review
    peer_review_env.initialize_submission(paper)
    rebuttal_done = False
    while not rebuttal_done:
        peer_review_env.step()
        rebuttal_done = peer_review_env.terminated
