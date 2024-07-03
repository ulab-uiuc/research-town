from unittest.mock import MagicMock, patch

import pytest
from beartype.typing import Any

from research_town.evaluators.quality_evaluator import (
    IdeaQualityEvaluator,
    PaperQualityEvaluator,
    ReviewQualityEvaluator,
)
from tests.eval_constants import (
    idea_constant_A,
    paper_abstract_constant_A,
    paper_title_constant_A,
    review_constant_A,
    review_constant_B,
    review_constant_C,
    review_constant_D,
    trend_constant_A,
)


@pytest.fixture(params=['gpt-4o', 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'])
def model_name(request: pytest.FixtureRequest) -> Any:
    return request.param


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_idea(use_mock: bool, model_name: str) -> None:
    evaluator = IdeaQualityEvaluator(model_name=model_name)
    input_dict = {'idea': idea_constant_A, 'trend': trend_constant_A, 'pk': 0}
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
            ), f"overall score of idea (mock) should be 86, but it's  {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of idea should be an Int between 0 and 100, but it's  {evals_output.overall_score}"


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_paper(use_mock: bool, model_name: str) -> None:
    paper = {'title': paper_title_constant_A, 'abstract': paper_abstract_constant_A}

    input_dict = {'idea': idea_constant_A, 'paper': paper, 'pk': 0}
    evaluator = PaperQualityEvaluator(model_name=model_name)
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
            ), f"overall score of paper (mock) should be 86, but it's  {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of paper should be an Int between 0 and 100, but it's  {evals_output.overall_score}"


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_review(use_mock: bool, model_name: str) -> None:
    paper = {'title': paper_title_constant_A, 'abstract': paper_abstract_constant_A}
    reviews = [
        review_constant_A,
        review_constant_B,
        review_constant_C,
        review_constant_D,
    ]
    input_dict = {
        'idea': idea_constant_A,
        'trend': trend_constant_A,
        'paper': paper,
        'pk': 0,
        'review': reviews,
        'decision': 'Reject',
    }
    evaluator = ReviewQualityEvaluator(model_name=model_name)
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
            ), f"overall score of paper (mock) should be 86, but it's  {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of paper should be an Int between 0 and 100, but it's  {evals_output.overall_score}"
