from unittest.mock import MagicMock, patch

from research_town.agents.agent_base import BaseResearchAgent
from research_town.dbs import AgentPaperRebuttalLog
from tests.constants import (
    agent_agent_discussion_log,
    agent_profile_A,
    agent_profile_B,
    paper_profile_A,
    paper_profile_B,
)
from tests.utils import mock_papers, mock_prompting


def test_get_profile() -> None:
    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    assert research_agent.profile.name == "Jiaxuan You"
    assert research_agent.profile.bio == "A researcher in the field of machine learning."


@patch("research_town.utils.agent_prompter.openai_prompting")
@patch("research_town.utils.agent_prompter.get_related_papers")
def test_generate_idea(
    mock_get_related_papers: MagicMock,
    mock_model_prompting: MagicMock,
) -> None:
    mock_get_related_papers.side_effect = mock_papers
    mock_model_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    ideas = research_agent.generate_idea(
        papers=[paper_profile_A, paper_profile_B],
        domain="machine learning"
    )
    assert ideas == ["This is a research idea."]


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_communicate(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "I believe in the potential of using automous agents to simulate the current research pipeline."
    ]

    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    response = research_agent.communicate(agent_agent_discussion_log)
    assert response.message == "I believe in the potential of using automous agents to simulate the current research pipeline."
    assert response.agent_to_pk is not None
    assert response.agent_from_pk is not None
    assert response.timestep >= 0
    assert response.pk is not None


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_write_paper(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = ["This is a paper abstract."]

    research_agent = BaseResearchAgent(agent_profile=agent_profile_B)
    paper = research_agent.write_paper(
        ["We can simulate the scientific research pipeline with agents."], [paper_profile_A])
    assert paper.abstract == "This is a paper abstract."
    assert paper.pk is not None


@patch("research_town.utils.agent_prompter.openai_prompting")
@patch("research_town.utils.agent_prompter.get_related_papers")
def test_read_paper(
    mock_get_related_papers: MagicMock,
    mock_model_prompting: MagicMock,
) -> None:
    mock_get_related_papers.side_effect = mock_papers
    mock_openai_prompting.side_effect = mock_prompting
    domain = "machine learning"
    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    summary = research_agent.read_paper([paper_profile_A], domain)
    assert summary == "Graph Neural Network"


@patch("research_town.utils.agent_prompter.model_prompting")
def test_find_collaborators(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = [
        "These are collaborators including Jure Leskovec, Rex Ying, Saining Xie, Kaiming He."]

    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    collaborators = research_agent.find_collaborators(
        paper=paper_profile_A, parameter=0.5, max_number=3)
    assert isinstance(collaborators, list)
    assert len(collaborators) <= 3


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_make_review_decision(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "Accept. This is a good paper."]

    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    review = research_agent.review_paper(paper=paper_profile_A)
    decision = research_agent.make_review_decision(
        paper=paper_profile_A, review=[review])
    assert decision.decision is True
    assert decision.meta_review == "Accept. This is a good paper."
    assert decision.timestep >= 0
    assert decision.pk is not None


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_review_paper(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    review = research_agent.review_paper(paper=paper_profile_A)
    assert review.review_score == 2
    assert review.review_content == "This is a paper review for MambaOut."

    
@patch("research_town.utils.agent_prompter.openai_prompting")
def test_rebut_review(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "This is a paper rebuttal."]

    research_agent = BaseResearchAgent(agent_profile=agent_profile_A)
    review = research_agent.review_paper(paper=paper_profile_A)
    decision = research_agent.make_review_decision(
        paper=paper_profile_A, review=[review])
    rebuttal = research_agent.rebut_review(
        paper=paper_profile_A, review=[review], decision=[decision])
    assert isinstance(rebuttal, AgentPaperRebuttalLog)
    if rebuttal.rebuttal_content is not None:
        assert len(rebuttal.rebuttal_content) > 0
    assert rebuttal.rebuttal_content == "This is a paper rebuttal."
