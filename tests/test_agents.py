from unittest.mock import MagicMock, patch

from research_town.agents.agent_base import BaseResearchAgent
from research_town.configs import Config
from research_town.dbs import AgentPaperRebuttalLog
from tests.db_constants import (
    agent_agent_discussion_log,
    agent_profile_A,
    agent_profile_B,
    paper_profile_A,
    paper_profile_B,
    research_idea_A,
    research_insight_A,
    research_insight_B,
)
from tests.utils import mock_papers, mock_prompting


def test_get_profile() -> None:
    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    assert research_agent.profile.name == 'Jiaxuan You'
    assert (
        research_agent.profile.bio == 'A researcher in the field of machine learning.'
    )


@patch('research_town.utils.agent_prompter.model_prompting')
def test_find_collaborators(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = [
        'These are collaborators including Jure Leskovec, Rex Ying, Saining Xie, Kaiming He.'
    ]

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    collaborators = research_agent.find_collaborators(
        paper=paper_profile_A, parameter=0.5, max_number=3, config=Config()
    )
    assert isinstance(collaborators, list)
    assert len(collaborators) <= 3


@patch('research_town.utils.agent_prompter.model_prompting')
@patch('research_town.utils.agent_prompter.get_related_papers')
def test_read_paper(
    mock_get_related_papers: MagicMock,
    mock_model_prompting: MagicMock,
) -> None:
    mock_get_related_papers.side_effect = mock_papers
    mock_model_prompting.side_effect = mock_prompting
    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    research_insight = research_agent.read_paper(
        papers=[paper_profile_A, paper_profile_B],
        domains=['machine learning', 'graph neural network'],
        config=Config(),
    )
    assert len(research_insight) == 1
    assert research_insight[0].pk is not None
    assert research_insight[0].content == 'Graph Neural Network'


@patch('research_town.utils.agent_prompter.model_prompting')
@patch('research_town.utils.agent_prompter.get_related_papers')
def test_think_idea(
    mock_get_related_papers: MagicMock,
    mock_model_prompting: MagicMock,
) -> None:
    mock_get_related_papers.side_effect = mock_papers
    mock_model_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    research_idea = research_agent.think_idea(
        insights=[research_insight_A, research_insight_B],
        config=Config(),
    )
    assert research_idea.pk is not None
    assert research_idea.content == 'This is a research idea.'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_paper(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = ['This is a paper abstract.']

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_B,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    paper = research_agent.write_paper(
        idea=research_idea_A,
        papers=[paper_profile_A, paper_profile_B],
        config=Config(),
    )
    assert paper.abstract == 'This is a paper abstract.'
    assert paper.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_paper_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    review = research_agent.write_paper_review(
        paper=paper_profile_A,
        config=Config(),
    )
    assert review.review_score == 2
    assert review.review_content == 'This is a paper review for MambaOut.'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_paper_meta_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = ['Accept. This is a good paper.']

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    reviews = research_agent.write_paper_review(
        paper=paper_profile_A,
        config=Config(),
    )
    meta_review = research_agent.write_paper_meta_review(
        paper=paper_profile_A,
        reviews=[reviews],
        config=Config(),
    )
    assert meta_review.decision is True
    assert meta_review.meta_review == 'Accept. This is a good paper.'
    assert meta_review.timestep >= 0
    assert meta_review.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_rebuttal(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = ['This is a paper rebuttal.']

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    review = research_agent.write_paper_review(
        paper=paper_profile_A,
        config=Config(),
    )
    rebuttal = research_agent.write_rebuttal(
        paper=paper_profile_A,
        review=review,
        config=Config(),
    )
    assert isinstance(rebuttal, AgentPaperRebuttalLog)
    if rebuttal.rebuttal_content is not None:
        assert len(rebuttal.rebuttal_content) > 0
    assert rebuttal.rebuttal_content == 'This is a paper rebuttal.'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_discuss(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = [
        'I believe in the potential of using automous agents to simulate the current research pipeline.'
    ]

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    response = research_agent.discuss(
        message=agent_agent_discussion_log,
        config=Config(),
    )
    assert (
        response.message
        == 'I believe in the potential of using automous agents to simulate the current research pipeline.'
    )
    assert response.agent_to_pk is not None
    assert response.agent_from_pk is not None
    assert response.timestep >= 0
    assert response.pk is not None
