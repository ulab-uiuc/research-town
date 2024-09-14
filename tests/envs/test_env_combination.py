from unittest.mock import MagicMock, patch

from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import Profile, ProfileDB, Proposal
from research_town.envs import ProposalWritingEnv, ReviewWritingEnv
from tests.constants.agent_constants import example_agent_manager
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
        config=Config(),
        agent_manager=example_agent_manager,
    )
    leader = example_agent_manager.create_leader(proposal_writing_agent_profiles[0])
    proposal_writing_env.on_enter(
        time_step=0,
        leader=leader,
    )
    run_result = proposal_writing_env.run()
    if run_result is not None:
        for progress, agent in run_result:
            pass
    exit_status, exit_dict = proposal_writing_env.on_exit()
    proposal = exit_dict['proposal']

    assert isinstance(proposal, Proposal)
    assert proposal.content == 'Paper abstract1'

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
        config=Config(),
        agent_manager=example_agent_manager,
    )
    leader = example_agent_manager.create_leader(review_writing_agent_profiles[0])
    review_writing_env.on_enter(
        time_step=0,
        proposal=proposal,
        leader=leader,
    )
    run_result = review_writing_env.run()
    if run_result is not None:
        for progress, agent in run_result:
            pass
    exit_status, _ = review_writing_env.on_exit()

    # Assertions for peer review environment
    assert exit_status == 'proposal_accept'

    meta_review = review_writing_env.meta_review
    assert meta_review is not None
