from unittest.mock import MagicMock, patch

from research_town.agents.agent_base import BaseResearchAgent
from research_town.configs import Config
from research_town.dbs import (
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReview,
    ResearchPaperSubmission,
    ResearchRebuttal,
    ResearchReview,
)
from tests.constants.data_constants import (
    agent_profile_A,
    agent_profile_B,
    paper_profile_A,
    paper_profile_B,
    research_idea_A,
    research_insight_A,
    research_insight_B,
    research_paper_submission_A,
)
from tests.mocks.mocking_func import mock_prompting


@patch('research_town.utils.agent_prompter.model_prompting')
def test_review_literature(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting
    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='proj_leader',
    )
    research_insight = research_agent.review_literature(
        papers=[paper_profile_A, paper_profile_B],
        domains=['machine learning', 'graph neural network'],
        config=Config(),
    )
    assert len(research_insight) == 3
    assert isinstance(research_insight[0], ResearchInsight)
    assert research_insight[0].pk is not None
    assert research_insight[0].content == 'Insight1'
    assert isinstance(research_insight[1], ResearchInsight)
    assert research_insight[1].pk is not None
    assert research_insight[1].content == 'Insight2'
    assert isinstance(research_insight[2], ResearchInsight)
    assert research_insight[2].pk is not None
    assert research_insight[2].content == 'Insight3'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_brainstorm_idea(
    mock_model_prompting: MagicMock,
) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='proj_leader',
    )
    research_idea = research_agent.brainstorm_idea(
        insights=[research_insight_A, research_insight_B],
        config=Config(),
    )
    assert isinstance(research_idea, ResearchIdea)
    assert research_idea.pk is not None
    assert research_idea.content == 'Idea1'


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_paper(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_B,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='proj_leader',
    )
    paper = research_agent.write_paper(
        idea=research_idea_A,
        papers=[paper_profile_A, paper_profile_B],
        config=Config(),
    )
    assert isinstance(paper, ResearchPaperSubmission)
    assert paper.abstract == 'Paper abstract1'
    assert paper.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='reviewer',
    )
    review = research_agent.write_review(
        paper=research_paper_submission_A,
        config=Config(),
    )
    assert isinstance(review, ResearchReview)
    assert review.summary == 'Summary of the paper1'
    assert review.strength == 'Strength of the paper1'
    assert review.weakness == 'Weakness of the paper1'
    assert review.score == 8


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_meta_review(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent_reviewer = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='reviewer',
    )
    research_agent_chair = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='chair',
    )
    research_agent_proj_leader = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='proj_leader',
    )
    review = research_agent_reviewer.write_review(
        paper=research_paper_submission_A,
        config=Config(),
    )
    rebuttal = research_agent_proj_leader.write_rebuttal(
        paper=research_paper_submission_A,
        review=review,
        config=Config(),
    )
    meta_review = research_agent_chair.write_meta_review(
        paper=research_paper_submission_A,
        reviews=[review],
        rebuttals=[rebuttal],
        config=Config(),
    )
    assert isinstance(meta_review, ResearchMetaReview)
    assert meta_review.summary == 'Meta review summary1'
    assert meta_review.strength == 'Meta review strength1'
    assert meta_review.weakness == 'Meta review weakness1'
    assert meta_review.decision is True
    assert meta_review.pk is not None


@patch('research_town.utils.agent_prompter.model_prompting')
def test_write_rebuttal(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    research_agent_reviewer = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='reviewer',
    )
    research_agent_proj_leader = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role='proj_leader',
    )
    review = research_agent_reviewer.write_review(
        paper=research_paper_submission_A,
        config=Config(),
    )
    rebuttal = research_agent_proj_leader.write_rebuttal(
        paper=research_paper_submission_A,
        review=review,
        config=Config(),
    )
    assert isinstance(rebuttal, ResearchRebuttal)
    if rebuttal.content is not None:
        assert len(rebuttal.content) > 0
    assert rebuttal.content == 'Rebuttal text1'
