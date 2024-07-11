from unittest.mock import MagicMock, patch

import pytest
from beartype.typing import Any

from research_town.configs import Config
from research_town.evaluators.quality_evaluator import (
    ResearchIdeaQualityEvaluator,
    ResearchInsightQualityEvaluator,
    ResearchMetaReviewQualityEvaluator,
    ResearchPaperSubmissionQualityEvaluator,
    ResearchRebuttalQualityEvaluator,
    ResearchReviewForPaperSubmissionQualityEvaluator,
)
from tests.constants.eval_constants import (
    idea_constant_A,
    paper_abstract_constant_A,
    paper_title_constant_A,
    review_constant_A,
    review_constant_B,
    review_constant_C,
    review_constant_D,
    trend_constant_A,
)

config_file_path = './configs/default_config.yaml'


@pytest.fixture(params=['gpt-4o', 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'])
def model_name(request: pytest.FixtureRequest) -> Any:
    return request.param


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_idea(use_mock: bool, model_name: str) -> None:
    config = Config(config_file_path)
    evaluator = ResearchIdeaQualityEvaluator(model_name=model_name, config=config)
    input_dict = {'idea': idea_constant_A, 'trend': trend_constant_A, 'pk': 0}
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
            ), f"overall score of idea (mock) should be 86, but it's  {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of idea should be an Int between 0 and 100, but it's  {evals_output.overall_score}"


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_paper(use_mock: bool, model_name: str) -> None:
    config = Config(config_file_path)
    paper = {'title': paper_title_constant_A, 'abstract': paper_abstract_constant_A}

    input_dict = {'idea': idea_constant_A, 'paper': paper, 'pk': 0}
    evaluator = ResearchPaperSubmissionQualityEvaluator(
        model_name=model_name, config=config
    )
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
            ), f"overall score of paper (mock) should be 86, but it's  {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of paper should be an Int between 0 and 100, but it's  {evals_output.overall_score}"


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_review(use_mock: bool, model_name: str) -> None:
    config = Config(config_file_path)
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
    evaluator = ResearchReviewForPaperSubmissionQualityEvaluator(
        model_name=model_name, config=config
    )
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
def test_evaluator_eval_insight(use_mock: bool, model_name: str) -> None:
    config = Config(config_file_path)
    evaluator = ResearchInsightQualityEvaluator(model_name=model_name, config=config)
    input_dict = {
        'insight': 'This is a research insight',
        'trend': trend_constant_A,
        'pk': 0,
    }
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
            ), f"overall score of insight (mock) should be 86, but it's {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of insight should be an Int between 0 and 100, but it's {evals_output.overall_score}"


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_rebuttal(use_mock: bool, model_name: str) -> None:
    config = Config(config_file_path)
    paper = {'title': paper_title_constant_A, 'abstract': paper_abstract_constant_A}
    reviews = [
        review_constant_A,
        review_constant_B,
        review_constant_C,
        review_constant_D,
    ]
    rebuttal = 'This is a rebuttal to the reviews'
    input_dict = {
        'idea': idea_constant_A,
        'trend': trend_constant_A,
        'paper': paper,
        'review': reviews,
        'rebuttal': rebuttal,
        'pk': 0,
    }
    evaluator = ResearchRebuttalQualityEvaluator(model_name=model_name, config=config)
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
            ), f"overall score of rebuttal (mock) should be 86, but it's {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of rebuttal should be an Int between 0 and 100, but it's {evals_output.overall_score}"


@pytest.mark.parametrize('use_mock', [True])
def test_evaluator_eval_meta_review(use_mock: bool, model_name: str) -> None:
    config = Config(config_file_path)
    paper = {'title': paper_title_constant_A, 'abstract': paper_abstract_constant_A}
    reviews = [
        review_constant_A,
        review_constant_B,
        review_constant_C,
        review_constant_D,
    ]
    meta_review = 'This is a meta-review of the paper submission'
    input_dict = {
        'idea': idea_constant_A,
        'trend': trend_constant_A,
        'paper': paper,
        'review': reviews,
        'meta_review': meta_review,
        'decision': 'Reject',
        'pk': 0,
    }
    evaluator = ResearchMetaReviewQualityEvaluator(model_name=model_name, config=config)
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
            ), f"overall score of meta-review (mock) should be 86, but it's {evals_output.overall_score}"
    else:
        evals_output = evaluator.eval(**input_dict)
        assert evals_output is not None
        assert (
            evals_output.overall_score >= 0 and evals_output.overall_score <= 100
        ), f"overall score of meta-review should be an Int between 0 and 100, but it's {evals_output.overall_score}"
