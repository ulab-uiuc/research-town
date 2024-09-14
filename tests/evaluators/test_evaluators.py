from unittest.mock import MagicMock, patch

import pytest
from beartype.typing import Any

from research_town.configs import Config
from research_town.evaluators.evaluator_quality import (
    IdeaQualityEvaluator,
    InsightQualityEvaluator,
    MetaReviewQualityEvaluator,
    ProposalQualityEvaluator,
    RebuttalQualityEvaluator,
    ReviewQualityEvaluator,
)
from tests.constants.data_constants import (
    research_idea_A,
    research_insight_A,
    research_insight_B,
    research_metareview_A,
    research_proposal_A,
    research_rebuttal_A,
    research_rebuttal_B,
    research_review_A,
    research_review_B,
)


@pytest.fixture(params=['gpt-4o', 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'])
def model_name(request: pytest.FixtureRequest) -> Any:
    return request.param


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_insight(use_mock: bool, model_name: str) -> None:
    config = Config()
    evaluator = InsightQualityEvaluator(model_name=model_name, config=config)

    insight = research_insight_A.model_dump()
    input_dict = {'insight': insight}

    if use_mock:
        with patch(
            'research_town.utils.eval_prompter.model_prompting',
            MagicMock(
                return_value=['Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8].']
            ),
        ):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output is not None
            assert (
                evals_output.overall_score == 86
            ), f'Expected 86, got {evals_output.overall_score}'
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            0 <= evals_output.overall_score <= 100
        ), f'Expected score between 0 and 100, got {evals_output.overall_score}'


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_idea(use_mock: bool, model_name: str) -> None:
    config = Config()
    evaluator = IdeaQualityEvaluator(model_name=model_name, config=config)
    insights = [research_insight_A.model_dump(), research_insight_B.model_dump()]
    idea = research_idea_A.model_dump()
    input_dict = {'insights': insights, 'idea': idea}

    if use_mock:
        with patch(
            'research_town.utils.eval_prompter.model_prompting',
            MagicMock(
                return_value=['Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8].']
            ),
        ):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output is not None
            assert (
                evals_output.overall_score == 86
            ), f'Expected 86, got {evals_output.overall_score}'
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            0 <= evals_output.overall_score <= 100
        ), f'Expected score between 0 and 100, got {evals_output.overall_score}'


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_paper(use_mock: bool, model_name: str) -> None:
    config = Config()
    insights = [research_insight_A.model_dump(), research_insight_B.model_dump()]
    idea = research_idea_A.model_dump()
    paper = research_proposal_A.model_dump()
    input_dict = {'insights': insights, 'idea': idea, 'paper': paper}

    evaluator = ProposalQualityEvaluator(model_name=model_name, config=config)

    if use_mock:
        with patch(
            'research_town.utils.eval_prompter.model_prompting',
            MagicMock(
                return_value=['Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8].']
            ),
        ):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output is not None
            assert (
                evals_output.overall_score == 86
            ), f'Expected 86, got {evals_output.overall_score}'
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            0 <= evals_output.overall_score <= 100
        ), f'Expected score between 0 and 100, got {evals_output.overall_score}'


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_review(use_mock: bool, model_name: str) -> None:
    config = Config()
    insights = [research_insight_A.model_dump(), research_insight_B.model_dump()]
    idea = research_idea_A.model_dump()
    paper = research_proposal_A.model_dump()
    review = research_review_A.model_dump()
    input_dict = {'insights': insights, 'idea': idea, 'paper': paper, 'review': review}

    evaluator = ReviewQualityEvaluator(model_name=model_name, config=config)

    if use_mock:
        with patch(
            'research_town.utils.eval_prompter.model_prompting',
            MagicMock(
                return_value=[
                    'Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8, 8, 9, 8, 8].'
                ]
            ),
        ):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output is not None
            assert (
                evals_output.overall_score == 86
            ), f'Expected 86, got {evals_output.overall_score}'
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            0 <= evals_output.overall_score <= 100
        ), f'Expected score between 0 and 100, got {evals_output.overall_score}'


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_rebuttal(use_mock: bool, model_name: str) -> None:
    config = Config()
    insights = [research_insight_A.model_dump(), research_insight_B.model_dump()]
    idea = research_idea_A.model_dump()
    paper = research_proposal_A.model_dump()
    review = research_review_A.model_dump()
    rebuttal = research_rebuttal_A.model_dump()
    input_dict = {
        'insights': insights,
        'idea': idea,
        'paper': paper,
        'review': review,
        'rebuttal': rebuttal,
    }

    evaluator = RebuttalQualityEvaluator(model_name=model_name, config=config)

    if use_mock:
        with patch(
            'research_town.utils.eval_prompter.model_prompting',
            MagicMock(
                return_value=[
                    'Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8, 8, 9, 8, 8].'
                ]
            ),
        ):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output is not None
            assert (
                evals_output.overall_score == 86
            ), f'Expected 86, got {evals_output.overall_score}'
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            0 <= evals_output.overall_score <= 100
        ), f'Expected score between 0 and 100, got {evals_output.overall_score}'


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_metareview(use_mock: bool, model_name: str) -> None:
    config = Config()
    insights = [research_insight_A.model_dump(), research_insight_B.model_dump()]
    idea = research_idea_A.model_dump()
    paper = research_proposal_A.model_dump()
    reviews = [research_review_A.model_dump(), research_review_B.model_dump()]
    rebuttals = [research_rebuttal_A.model_dump(), research_rebuttal_B.model_dump()]
    metareview = research_metareview_A.model_dump()
    input_dict = {
        'insights': insights,
        'idea': idea,
        'paper': paper,
        'reviews': reviews,
        'rebuttals': rebuttals,
        'metareview': metareview,
    }

    evaluator = MetaReviewQualityEvaluator(model_name=model_name, config=config)

    if use_mock:
        with patch(
            'research_town.utils.eval_prompter.model_prompting',
            MagicMock(
                return_value=[
                    'Overall Score=86. Dimension Scores=[9, 8, 9, 9, 8, 8, 8, 9, 8, 8].'
                ]
            ),
        ):
            evals_output = evaluator.eval(**input_dict)
            assert evals_output is not None
            assert (
                evals_output.overall_score == 86
            ), f'Expected 86, got {evals_output.overall_score}'
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            0 <= evals_output.overall_score <= 100
        ), f'Expected score between 0 and 100, got {evals_output.overall_score}'
