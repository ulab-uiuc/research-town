import re

from beartype.typing import Any, Type, TypeVar
from pydantic import BaseModel

from ..utils.error_handler import parsing_error_exponential_backoff
from ..utils.eval_prompter import (
    idea_quality_eval_prompting,
    paper_quality_eval_prompting,
    review_quality_eval_prompting,
)
from .evaluator_output import (
    ResearchIdeaEvalOutput,
    ResearchPaperSubmissionEvalOutput,
    ResearchReviewForPaperSubmissionEvalOutput,
)
from .evaluator_output_format import OutputFormatError

T = TypeVar('T', bound=BaseModel)


class BaseQualityEvaluator:
    def __init__(
        self, model_name: str, output_model: Type[T], *args: Any, **kwargs: Any
    ) -> None:
        self.model_name = model_name
        self.parsed_output = output_model()

    def eval(self, *args: Any, **kwargs: Any) -> T:
        raise NotImplementedError('Subclasses should implement this method')

    def parse(self, raw_output: str, output_model: Type[T]) -> T:
        overall_score_match = re.search(
            r'Overall\s*Score\s*\W*(\d+)\W*', raw_output, re.IGNORECASE
        )
        dimension_scores_match = re.search(
            r'Dimension\s*Scores\s*\W*\s*\[([0-9,\s]+)\]', raw_output, re.IGNORECASE
        )

        if overall_score_match:
            try:
                overall_score = int(overall_score_match.group(1))
            except ValueError as e:
                raise OutputFormatError(f'Invalid overall score: {e}')
        else:
            raise OutputFormatError(
                f"Output format error: 'Overall Score' not found. Raw output is {raw_output}."
            )

        if dimension_scores_match:
            try:
                dimension_scores = list(
                    map(int, dimension_scores_match.group(1).split(','))
                )
            except ValueError as e:
                raise OutputFormatError(f'Invalid dimension scores: {e}')
        else:
            raise OutputFormatError(
                f"Output format error: 'Dimension Scores' not found. Raw output is {raw_output}."
            )

        return output_model(
            overall_score=overall_score, dimension_scores=dimension_scores
        )


class ResearchIdeaQualityEvaluator(BaseQualityEvaluator):
    def __init__(self, model_name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(model_name, ResearchIdeaEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchIdeaEvalOutput:
        raw_output = idea_quality_eval_prompting(
            idea=kwargs['idea'], trend=kwargs['trend'], model_name=self.model_name
        )
        self.parsed_output = self.parse(raw_output, ResearchIdeaEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchPaperSubmissionQualityEvaluator(BaseQualityEvaluator):
    def __init__(self, model_name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(model_name, ResearchPaperSubmissionEvalOutput, *args, **kwargs)

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(self, *args: Any, **kwargs: Any) -> ResearchPaperSubmissionEvalOutput:
        raw_output = paper_quality_eval_prompting(
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            model_name=self.model_name,
            trend=kwargs.get('trend'),
        )
        self.parsed_output = self.parse(raw_output, ResearchPaperSubmissionEvalOutput)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output


class ResearchReviewForPaperSubmissionQualityEvaluator(BaseQualityEvaluator):
    def __init__(self, model_name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            model_name, ResearchReviewForPaperSubmissionEvalOutput, *args, **kwargs
        )

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(
        self, *args: Any, **kwargs: Any
    ) -> ResearchReviewForPaperSubmissionEvalOutput:
        raw_output = review_quality_eval_prompting(
            idea=kwargs['idea'],  # idea: str,
            trend=kwargs['trend'],  # trend: str,
            paper=kwargs['paper'],  # paper: Dict[str,str],
            review=kwargs['review'],  # review: List[str],
            decision=kwargs['decision'],  # decision: str,
            model_name=self.model_name,
            rebuttal=kwargs.get('rebuttal'),  # rebuttal: str,
            meta_review=kwargs.get('meta_review'),  # meta_review: str,
        )
        self.parsed_output = self.parse(
            raw_output, ResearchReviewForPaperSubmissionEvalOutput
        )

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output
