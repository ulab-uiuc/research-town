from unittest.mock import MagicMock, patch

from research_town.agents.agent_base import ResearchAgent
from research_town.agents.agent_role import Role
from research_town.configs import Config
from research_town.dbs import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from tests.constants.data_constants import (
    agent_profile_A,
    agent_profile_B,
    paper_profile_A,
    paper_profile_B,
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
    research_agent = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.LEADER,
    )
    research_insight = research_agent.review_literature(
        papers=[paper_profile_A, paper_profile_B],
        domains=['machine learning', 'graph neural network'],
        config=Config(),
    )
    assert len(research_insight) == 3
    assert isinstance(research_insight[0], Insight)
    assert research_insight[0].pk is not None
    assert research_insight[0].content == 'Insight1'
    assert isinstance(research_insight[1], Insight)
    assert research_insight[1].pk is not None
    assert research_insight[1].content == 'Insight2'
    assert isinstance(research_insight[2], Insight)
    assert research_insight[2].pk is not None
    assert research_insight[2].content == 'Insight3'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_brainstorm_idea(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.LEADER,
    )
    research_idea = research_agent.brainstorm_idea(
        insights=[research_insight_A, research_insight_B],
        config=Config(),
    )
    assert isinstance(research_idea, Idea)
    assert research_idea.pk is not None
    assert research_idea.content == 'Idea1'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_proposal(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent = ResearchAgent(
        agent_profile=agent_profile_B,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.LEADER,
    )
    paper = research_agent.write_proposal(
        idea=research_idea_A,
        papers=[paper_profile_A, paper_profile_B],
        config=Config(),
    )
    assert isinstance(paper, Proposal)
    assert paper.abstract == 'Paper abstract1'
    assert paper.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.REVIEWER,
    )
    review = research_agent.write_review(
        paper=research_proposal_A,
        config=Config(),
    )
    assert isinstance(review, Review)
    assert review.summary == 'Summary of the paper1'
    assert review.strength == 'Strength of the paper1'
    assert review.weakness == 'Weakness of the paper1'
    assert review.score == 8


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_meta_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent_reviewer = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.REVIEWER,
    )
    research_agent_chair = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.CHAIR,
    )
    research_agent_leader = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.LEADER,
    )
    review = research_agent_reviewer.write_review(
        paper=research_proposal_A,
        config=Config(),
    )
    rebuttal = research_agent_leader.write_rebuttal(
        paper=research_proposal_A,
        review=review,
        config=Config(),
    )
    meta_review = research_agent_chair.write_meta_review(
        paper=research_proposal_A,
        reviews=[review],
        rebuttals=[rebuttal],
        config=Config(),
    )
    assert isinstance(meta_review, MetaReview)
    assert meta_review.summary == 'Meta review summary1'
    assert meta_review.strength == 'Meta review strength1'
    assert meta_review.weakness == 'Meta review weakness1'
    assert meta_review.decision is True
    assert meta_review.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_rebuttal(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent_reviewer = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.REVIEWER,
    )
    research_agent_leader = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.LEADER,
    )
    review = research_agent_reviewer.write_review(
        paper=research_proposal_A,
        config=Config(),
    )
    rebuttal = research_agent_leader.write_rebuttal(
        paper=research_proposal_A,
        review=review,
        config=Config(),
    )
    assert isinstance(rebuttal, Rebuttal)
    if rebuttal.content is not None:
        assert len(rebuttal.content) > 0
    assert rebuttal.content == 'Rebuttal text1'
