import datetime
from unittest.mock import MagicMock, patch

from beartype.typing import List

from research_town.agents import AgentManager
from research_town.data import Profile, Proposal
from research_town.dbs import ProfileDB
from research_town.envs import ProposalWritingwithRAGEnv, ReviewWritingEnv
from tests.constants.config_constants import example_config
from tests.constants.db_constants import (
    example_log_db,
    example_paper_db,
    example_progress_db,
)
from tests.mocks.mocking_func import mock_prompting


@patch('research_town.utils.agent_prompter.model_prompting')
@patch('arxiv.Client')
def test_env_combo(mock_client: MagicMock, mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance

    mock_paper_1 = MagicMock()
    mock_paper_1.title = 'Paper 1'
    mock_paper_1.entry_id = 'http://example.com/1'
    mock_paper_1.summary = 'Summary 1'
    mock_paper_1.primary_category = 'cs'
    mock_paper_1.published = datetime.datetime(2023, 7, 1)

    mock_paper_2 = MagicMock()
    mock_paper_2.title = 'Paper 2'
    mock_paper_2.entry_id = 'http://example.com/2'
    mock_paper_2.summary = 'Summary 2'
    mock_paper_2.primary_category = 'cs'
    mock_paper_2.published = datetime.datetime(2023, 7, 2)

    mock_client_instance.results.return_value = [mock_paper_1, mock_paper_2]

    proposal_writing_profiles = [
        Profile(name='Jiaxuan You', bio='A researcher in machine learning.'),
        Profile(name='Rex Ying', bio='A researcher in natural language processing.'),
        Profile(name='Rex Zhu', bio='A researcher in computer vision.'),
        Profile(name='Rex Wang', bio='A researcher in computer vision.'),
        Profile(name='Rex Li', bio='A researcher in computer vision.'),
        Profile(name='Rex Yu', bio='A researcher in computer vision.'),
    ]

    temp_profile_db = ProfileDB()
    for profile in proposal_writing_profiles:
        temp_profile_db.add(profile)

    agent_manager = AgentManager(config=example_config, profile_db=temp_profile_db)

    proposal_writing_env = ProposalWritingwithRAGEnv(
        name='proposal_writing',
        paper_db=example_paper_db,
        log_db=example_log_db,
        progress_db=example_progress_db,
        config=example_config,
        agent_manager=agent_manager,
    )
    leader = agent_manager.create_agent(
        profile=proposal_writing_profiles[0], role='leader'
    )
    proposal_writing_env.on_enter(
        time_step=0,
        leader=leader,
        contexts=[
            "Much of the world's most valued data is stored in relational databases and data warehouses, where the data is organized into many tables connected by primary-foreign key relations. However, building machine learning models using this data is both challenging and time consuming. The core problem is that no machine learning method is capable of learning on multiple tables interconnected by primary-foreign key relations. Current methods can only learn from a single table, so the data must first be manually joined and aggregated into a single training table, the process known as feature engineering. Feature engineering is slow, error prone and leads to suboptimal models. Here we introduce an end-to-end deep representation learning approach to directly learn on data laid out across multiple tables. We name our approach Relational Deep Learning (RDL). The core idea is to view relational databases as a temporal, heterogeneous graph, with a node for each row in each table, and edges specified by primary-foreign key links. Message Passing Graph Neural Networks can then automatically learn across the graph to extract representations that leverage all input data, without any manual feature engineering. Relational Deep Learning leads to more accurate models that can be built much faster. To facilitate research in this area, we develop RelBench, a set of benchmark datasets and an implementation of Relational Deep Learning. The data covers a wide spectrum, from discussions on Stack Exchange to book reviews on the Amazon Product Catalog. Overall, we define a new research area that generalizes graph machine learning and broadens its applicability to a wide set of AI use cases."
        ],
    )
    run_result = proposal_writing_env.run()
    if run_result is not None:
        for progress, agent in run_result:
            pass
    exit_status, exit_dict = proposal_writing_env.on_exit()
    proposals = exit_dict['proposals']

    for proposal in proposals:
        assert isinstance(proposal, Proposal)
        assert proposal.content == 'Paper abstract1'

    review_writing_agent_list: List[str] = [
        'Jiaxuan You',
        'Jure Leskovec',
        'Geoffrey Hinton',
    ]
    review_writing_profiles = [
        Profile(name=agent, bio='A researcher in machine learning.')
        for agent in review_writing_agent_list
    ]

    temp_profile_db = ProfileDB()
    for profile in review_writing_profiles:
        temp_profile_db.add(profile)

    review_writing_env = ReviewWritingEnv(
        name='review_writing',
        paper_db=example_paper_db,
        log_db=example_log_db,
        progress_db=example_progress_db,
        config=example_config,
        agent_manager=agent_manager,
    )
    leader = agent_manager.create_agent(
        profile=review_writing_profiles[0], role='leader'
    )
    review_writing_env.on_enter(
        time_step=0,
        proposals=proposals,
        leader=leader,
    )
    run_result = review_writing_env.run()
    if run_result is not None:
        for progress, agent in run_result:
            pass
    exit_status, _ = review_writing_env.on_exit()

    assert exit_status == 'proposal_accept'

    metareviews = review_writing_env.metareviews
    assert metareviews is not None

    assert len(mock_client_instance.results.return_value) == 2
