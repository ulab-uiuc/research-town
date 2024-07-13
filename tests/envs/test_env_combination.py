from unittest.mock import MagicMock, patch

from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import (
    AgentProfile,
    ResearchMetaReviewForPaperSubmission,
    ResearchPaperSubmission,
    ResearchRebuttalForPaperSubmission,
    ResearchReviewForPaperSubmission,
)
from research_town.envs import PaperSubmissionMultiAgentEnv, PeerReviewMultiAgentEnv
from tests.constants.db_constants import (
    example_env_db,
    example_paper_db,
    example_progress_db,
)
from tests.mocks.mocking_func import mock_prompting

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_env_combo(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    # Agent profiles and roles for paper submission environment
    paper_submission_role_list: List[Role] = [
        'proj_leader',
        'proj_participant',
        'proj_participant',
    ]
    paper_submission_agent_profiles = [
        AgentProfile(name='Jiaxuan You', bio='A researcher in machine learning.'),
        AgentProfile(
            name='Rex Ying', bio='A researcher in natural language processing.'
        ),
        AgentProfile(name='Rex Zhu', bio='A researcher in computer vision.'),
    ]

    # Create and run the paper submission environment
    paper_submission_env = PaperSubmissionMultiAgentEnv(
        paper_db=example_paper_db,
        env_db=example_env_db,
        progress_db=example_progress_db,
        config=Config(),
    )
    paper_submission_env.on_enter(
        time_step=0,
        stop_flag=False,
        agent_profiles=paper_submission_agent_profiles,
        agent_roles=paper_submission_role_list,
        agent_models=['together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'],
    )
    paper_submission_env.run()
    paper = paper_submission_env.paper

    assert isinstance(paper, ResearchPaperSubmission)
    assert paper.abstract == 'Paper abstract1'

    # Agent profiles and roles for peer review environment
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

    # Create and run the peer review environment
    peer_review_env = PeerReviewMultiAgentEnv(
        paper_db=example_paper_db,
        env_db=example_env_db,
        progress_db=example_progress_db,
        config=Config(),
    )
    peer_review_env.on_enter(
        time_step=0,
        stop_flag=False,
        agent_profiles=peer_review_agent_profiles,
        agent_roles=peer_review_role_list,
        agent_models=[
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        ],
        paper=paper,
    )
    peer_review_env.run()
    exit_status = peer_review_env.on_exit()

    # Assertions for peer review environment
    assert exit_status is True

    meta_review, rebuttals, reviews = (
        peer_review_env.meta_review,
        peer_review_env.rebuttals,
        peer_review_env.reviews,
    )

    assert isinstance(meta_review, ResearchMetaReviewForPaperSubmission)
    assert meta_review.paper_pk == paper.pk
    assert meta_review.decision is True
    assert meta_review.weakness == 'Meta review weakness1'
    assert meta_review.strength == 'Meta review strength1'
    assert meta_review.summary == 'Meta review summary1'

    assert isinstance(reviews, list)
    assert len(reviews) == 1
    assert isinstance(reviews[0], ResearchReviewForPaperSubmission)
    assert reviews[0].paper_pk == paper.pk
    assert reviews[0].score == 8
    assert reviews[0].weakness == 'Weakness of the paper1'
    assert reviews[0].strength == 'Strength of the paper1'
    assert reviews[0].summary == 'Summary of the paper1'

    assert isinstance(rebuttals, list)
    assert len(rebuttals) == 1
    assert isinstance(rebuttals[0], ResearchRebuttalForPaperSubmission)
    assert rebuttals[0].content == 'Rebuttal text1'
    assert rebuttals[0].paper_pk == paper.pk
