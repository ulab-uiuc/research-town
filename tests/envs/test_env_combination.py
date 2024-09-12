from unittest.mock import MagicMock, patch

from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import Profile, ProfileDB, Proposal, Review
from research_town.envs import ProposalWritingEnv, ReviewWritingEnv
from tests.constants.db_constants import (
    example_log_db,
    example_paper_db,
    example_progress_db,
)
from tests.mocks.mocking_func import mock_prompting

Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_env_combo(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    proposal_writing_agent_profiles = [
        Profile(name='Jiaxuan You', bio='A researcher in machine learning.'),
        Profile(name='Rex Ying', bio='A researcher in natural language processing.'),
        Profile(name='Rex Zhu', bio='A researcher in computer vision.'),
    ]

    temp_profile_db = ProfileDB()
    for profile in proposal_writing_agent_profiles:
        temp_profile_db.add(profile)

    # Create and run the paper submission environment
    proposal_writing_env = ProposalWritingEnv(
        name='proposal_writing',
        paper_db=example_paper_db,
        log_db=example_log_db,
        progress_db=example_progress_db,
        profile_db=temp_profile_db,
        config=Config(),
    )
    proposal_writing_env.on_enter(
        time_step=0,
        leader_profile=proposal_writing_agent_profiles[0],
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
    review_writing_agent_profiles = [
        Profile(name=agent, bio='A researcher in machine learning.')
        for agent in review_writing_agent_list
    ]

    temp_profile_db = ProfileDB()
    for profile in review_writing_agent_profiles:
        temp_profile_db.add(profile)

    # Create and run the peer review environment
    review_writing_env = ReviewWritingEnv(
        name='review_writing',
        paper_db=example_paper_db,
        log_db=example_log_db,
        progress_db=example_progress_db,
        profile_db=temp_profile_db,
        config=Config(),
    )
    review_writing_env.on_enter(
        time_step=0,
        proposal=paper,
        leader_profile=review_writing_agent_profiles[0],
    )
    review_writing_env.run()
    exit_status = review_writing_env.on_exit()

    # Assertions for peer review environment
    assert exit_status == 'proposal_accept'

    reviews = review_writing_env.reviews

    assert isinstance(reviews, list)
    assert len(reviews) == 1
    assert isinstance(reviews[0], Review)
    assert reviews[0].paper_pk == paper.pk
    assert reviews[0].score == 8
    assert reviews[0].weakness == 'Weakness of the paper1'
    assert reviews[0].strength == 'Strength of the paper1'
    assert reviews[0].summary == 'Summary of the paper1'
