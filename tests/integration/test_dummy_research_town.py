from unittest.mock import MagicMock, patch

from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfileDB,
    ProgressDB,
    ResearchMetaReviewForPaperSubmission,
    ResearchPaperSubmission,
    ResearchRebuttalForPaperSubmission,
    ResearchReviewForPaperSubmission,
)
from research_town.envs import PaperSubmissionMultiAgentEnv, PeerReviewMultiAgentEnv
from tests.mocks.mocking_func import mock_prompting

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_dummy_research_town(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    paper_submission_agent_list: List[str] = ['Jiaxuan You']
    paper_submission_role_list: List[Role] = ['proj_leader']
    paper_submission_agent_profiles = [
        AgentProfile(name=agent, bio='A researcher in machine learning.')
        for agent in paper_submission_agent_list
    ]

    agent_db = AgentProfileDB()
    paper_db = PaperProfileDB()
    env_db = EnvLogDB()
    progress_db = ProgressDB()
    config = Config()
    paper_submission_env = PaperSubmissionMultiAgentEnv(
        agent_profiles=paper_submission_agent_profiles,
        agent_roles=paper_submission_role_list,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )

    peer_review_agent_list: List[str] = [
        'Jiaxuan You',
        'Jure Leskovec',
        'Geoffrey Hinton',
    ]
    peer_review_role_list: List[Role] = ['proj_leader', 'reviewer', 'chair']
    peer_review_agent_profiles = [
        AgentProfile(name=agent, bio='A researcher in machine learning.')
        for agent in peer_review_agent_list
    ]
    peer_review_env = PeerReviewMultiAgentEnv(
        agent_profiles=peer_review_agent_profiles,
        agent_roles=peer_review_role_list,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )

    paper = paper_submission_env.run()

    assert isinstance(paper, ResearchPaperSubmission)
    assert paper.abstract == 'Paper abstract'

    meta_review, rebuttals, reviews = peer_review_env.run(paper)

    assert isinstance(meta_review, ResearchMetaReviewForPaperSubmission)
    assert meta_review.paper_pk == paper.pk
    assert meta_review.decision is True
    assert meta_review.weakness == 'Meta review weakness'
    assert meta_review.strength == 'Meta review strength'
    assert meta_review.summary == 'Meta review summary'

    assert isinstance(reviews, list)
    assert len(reviews) == 1
    assert isinstance(reviews[0], ResearchReviewForPaperSubmission)
    assert reviews[0].paper_pk == paper.pk
    assert reviews[0].score == 8
    assert reviews[0].weakness == 'Weakness of the paper'
    assert reviews[0].strength == 'Strength of the paper'
    assert reviews[0].summary == 'Summary of the paper'

    assert isinstance(rebuttals, list)
    assert len(rebuttals) == 1
    assert isinstance(rebuttals[0], ResearchRebuttalForPaperSubmission)
    assert rebuttals[0].content == 'Rebuttal text'
    assert rebuttals[0].paper_pk == paper.pk
