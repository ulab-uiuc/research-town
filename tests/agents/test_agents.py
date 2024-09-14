from typing import List
from unittest.mock import MagicMock, patch

from research_town.agents.agent import Agent
from research_town.configs import Config
from research_town.dbs import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from tests.constants.data_constants import (
    agent_profile_A,
    agent_profile_B,
    paper_A,
    paper_B,
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
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='leader',
    )
    research_insight = agent.review_literature(
        papers=[paper_A, paper_B],
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

    agent = Agent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='leader',
    )
    research_idea = agent.brainstorm_idea(
        insights=[research_insight_A, research_insight_B],
        config=Config(),
    )
    assert isinstance(research_idea, Idea)
    assert research_idea.pk is not None
    assert research_idea.content == 'Idea1'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_proposal(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    agent = Agent(
        agent_profile=agent_profile_B,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='leader',
    )
    paper = agent.write_proposal(
        idea=research_idea_A,
        papers=[paper_A, paper_B],
        config=Config(),
    )
    assert isinstance(paper, List[Proposal])
    assert paper.content == 'Paper abstract1'
    assert paper.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    agent = Agent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='reviewer',
    )
    review = agent.write_review(
        paper=research_proposal_A,
        config=Config(),
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
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='reviewer',
    )
    agent_chair = Agent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='chair',
    )
    agent_leader = Agent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='leader',
    )
    review = agent_reviewer.write_review(
        paper=research_proposal_A,
        config=Config(),
    )
    rebuttal = agent_leader.write_rebuttal(
        paper=research_proposal_A,
        review=review,
        config=Config(),
    )
    metareview = agent_chair.write_metareview(
        paper=research_proposal_A,
        reviews=[review],
        rebuttals=[rebuttal],
        config=Config(),
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
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='reviewer',
    )
    agent_leader = Agent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='leader',
    )
    review = agent_reviewer.write_review(
        paper=research_proposal_A,
        config=Config(),
    )
    rebuttal = agent_leader.write_rebuttal(
        paper=research_proposal_A,
        review=review,
        config=Config(),
    )
    assert isinstance(rebuttal, Rebuttal)
    if rebuttal.content is not None:
        assert len(rebuttal.content) > 0
    assert rebuttal.content == 'Rebuttal text1'
