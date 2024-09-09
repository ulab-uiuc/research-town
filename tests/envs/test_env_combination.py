from unittest.mock import MagicMock, patch

from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import Proposal, Researcher, Review
from research_town.envs import ProposalWritingEnv, ReviewWritingEnv
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
    proposal_writing_role_list: List[Role] = [
        'proj_leader',
        'proj_participant',
        'proj_participant',
    ]
    proposal_writing_agent_profiles = [
        Researcher(name='Jiaxuan You', bio='A researcher in machine learning.'),
        Researcher(name='Rex Ying', bio='A researcher in natural language processing.'),
        Researcher(name='Rex Zhu', bio='A researcher in computer vision.'),
    ]

    # Create and run the paper submission environment
    proposal_writing_env = ProposalWritingEnv(
        paper_db=example_paper_db,
        env_db=example_env_db,
        progress_db=example_progress_db,
        config=Config(),
    )
    proposal_writing_env.on_enter(
        time_step=0,
        stop_flag=False,
        agent_profiles=proposal_writing_agent_profiles,
        agent_roles=proposal_writing_role_list,
        agent_models=['together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'],
    )
    proposal_writing_env.run()
    paper = proposal_writing_env.proposal

    assert isinstance(paper, Proposal)
    assert paper.abstract == 'Paper abstract1'

    # Agent profiles and roles for peer review environment
    review_writing_agent_list: List[str] = [
        'Jiaxuan You',
        'Jure Leskovec',
        'Geoffrey Hinton',
    ]
    review_writing_role_list: List[Role] = ['proj_leader', 'reviewer', 'chair']
    review_writing_agent_profiles = [
        Researcher(name=agent, bio='A researcher in machine learning.')
        for agent in review_writing_agent_list
    ]

    # Create and run the peer review environment
    review_writing_env = ReviewWritingEnv(
        paper_db=example_paper_db,
        env_db=example_env_db,
        progress_db=example_progress_db,
        config=Config(),
    )
    review_writing_env.on_enter(
        time_step=0,
        stop_flag=False,
        agent_profiles=review_writing_agent_profiles,
        agent_roles=review_writing_role_list,
        agent_models=[
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
            'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        ],
        paper=paper,
    )
    review_writing_env.run()
    exit_status = review_writing_env.on_exit()

    # Assertions for peer review environment
    assert exit_status is True

    reviews = review_writing_env.reviews

    assert isinstance(reviews, list)
    assert len(reviews) == 1
    assert isinstance(reviews[0], Review)
    assert reviews[0].paper_pk == paper.pk
    assert reviews[0].score == 8
    assert reviews[0].weakness == 'Weakness of the paper1'
    assert reviews[0].strength == 'Strength of the paper1'
    assert reviews[0].summary == 'Summary of the paper1'
