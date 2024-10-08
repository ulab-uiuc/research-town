from unittest.mock import MagicMock, patch

from research_town.agents.agent import Agent
from research_town.data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from tests.constants.config_constants import example_config
from tests.constants.data_constants import (
    paper_A,
    paper_B,
    profile_A,
    profile_B,
    research_idea_A,
    research_insight_A,
    research_insight_B,
    research_proposal_A,
)
from tests.mocks.mocking_func import mock_prompting


@patch('research_town.utils.agent_prompter.model_prompting')
def test_review_literature(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting
    agent = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role='leader',
    )
    _, _, research_insight, _ = agent.review_literature(
        papers=[paper_A, paper_B],
        contexts=[
            "Much of the world's most valued data is stored in relational databases and data warehouses, where the data is organized into many tables connected by primary-foreign key relations. However, building machine learning models using this data is both challenging and time consuming. The core problem is that no machine learning method is capable of learning on multiple tables interconnected by primary-foreign key relations. Current methods can only learn from a single table, so the data must first be manually joined and aggregated into a single training table, the process known as feature engineering. Feature engineering is slow, error prone and leads to suboptimal models. Here we introduce an end-to-end deep representation learning approach to directly learn on data laid out across multiple tables. We name our approach Relational Deep Learning (RDL). The core idea is to view relational databases as a temporal, heterogeneous graph, with a node for each row in each table, and edges specified by primary-foreign key links. Message Passing Graph Neural Networks can then automatically learn across the graph to extract representations that leverage all input data, without any manual feature engineering. Relational Deep Learning leads to more accurate models that can be built much faster. To facilitate research in this area, we develop RelBench, a set of benchmark datasets and an implementation of Relational Deep Learning. The data covers a wide spectrum, from discussions on Stack Exchange to book reviews on the Amazon Product Catalog. Overall, we define a new research area that generalizes graph machine learning and broadens its applicability to a wide set of AI use cases."
        ],
        config=example_config,
    )
    assert isinstance(research_insight, Insight)
    assert research_insight.pk is not None
    assert research_insight.content == 'Insight1'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_brainstorm_idea(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting
    agent = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role='leader',
    )
    research_idea, _ = agent.brainstorm_idea(
        insights=[research_insight_A, research_insight_B],
        papers=[paper_A, paper_B],
        config=example_config,
    )
    assert isinstance(research_idea, Idea)
    assert research_idea.pk is not None
    assert research_idea.content == 'Idea1'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_proposal(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting
    agent = Agent(
        profile=profile_B,
        model_name='gpt-4o-mini',
        role='leader',
    )
    paper, _ = agent.write_proposal(
        idea=research_idea_A,
        papers=[paper_A, paper_B],
        config=example_config,
    )
    assert isinstance(paper, Proposal)
    assert paper.content == 'Paper abstract1'
    assert paper.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting
    agent = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role='reviewer',
    )
    review, _ = agent.write_review(
        proposal=research_proposal_A,
        config=example_config,
    )
    assert isinstance(review, Review)
    assert review.summary == 'Summary of the paper1'
    assert review.strength == 'Strength of the paper1'
    assert review.weakness == 'Weakness of the paper1'
    assert review.score == 8


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_metareview(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting
    agent_reviewer = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role='reviewer',
    )
    agent_chair = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role='chair',
    )
    review, _ = agent_reviewer.write_review(
        proposal=research_proposal_A,
        config=example_config,
    )
    metareview, _ = agent_chair.write_metareview(
        proposal=research_proposal_A,
        reviews=[review],
        config=example_config,
    )
    assert isinstance(metareview, MetaReview)
    assert metareview.summary == 'Meta review summary1'
    assert metareview.strength == 'Meta review strength1'
    assert metareview.weakness == 'Meta review weakness1'
    assert metareview.decision is True
    assert metareview.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_rebuttal(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting
    agent_reviewer = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role='reviewer',
    )
    agent_leader = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role='leader',
    )
    review, _ = agent_reviewer.write_review(
        proposal=research_proposal_A,
        config=example_config,
    )
    rebuttal, _ = agent_leader.write_rebuttal(
        proposal=research_proposal_A,
        review=review,
        config=example_config,
    )
    assert isinstance(rebuttal, Rebuttal)
    if rebuttal.content is not None:
        assert len(rebuttal.content) > 0
    assert rebuttal.content == 'Rebuttal text1'
