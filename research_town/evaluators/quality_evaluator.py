import re

from beartype.typing import Any

from ..utils.error_handler import parsing_error_exponential_backoff
from ..utils.eval_prompter import (
    idea_quality_eval_prompting,
    paper_quality_eval_prompting,
    review_quality_eval_prompting,
)
from .output_format import (
    IdeaEvalOutput,
    OutputFormatError,
    PaperEvalOutput,
    ReviewEvalOutput,
)


class IdeaQualityEvaluator(object):
    def __init__(self, model_name: str, *args: Any, **kwargs: Any) -> None:
        self.model_name = model_name
        self.parsed_output = IdeaEvalOutput()

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> IdeaEvalOutput:
        raw_output = idea_quality_eval_prompting(
            idea=kwargs['idea'], trend=kwargs['trend'], model_name=self.model_name
        )
        self.parsed_output = self.parse(raw_output)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output: str) -> IdeaEvalOutput:
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
        return IdeaEvalOutput(
            overall_score=overall_score, dimension_scores=dimension_scores
        )


class PaperQualityEvaluator(object):
    def __init__(self, model_name: str, *args: Any, **kwargs: Any) -> None:
        self.model_name = model_name
        self.parsed_output = PaperEvalOutput()

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> PaperEvalOutput:
        raw_output = paper_quality_eval_prompting(
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            model_name=self.model_name,
            trend=kwargs['trend'] if 'trend' in kwargs else None,
        )
        self.parsed_output = self.parse(raw_output)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output: str) -> PaperEvalOutput:
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
        return PaperEvalOutput(
            overall_score=overall_score, dimension_scores=dimension_scores
        )


class ReviewQualityEvaluator(object):
    def __init__(self, model_name: str, *args: Any, **kwargs: Any) -> None:
        self.model_name = model_name
        self.parsed_output = ReviewEvalOutput()

    @parsing_error_exponential_backoff(retries=5, base_wait_time=1)
    def eval(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> ReviewEvalOutput:
        raw_output = review_quality_eval_prompting(
            idea=kwargs['idea'],  # idea: str,
            trend=kwargs['trend'],  # trend: str,
            paper=kwargs['paper'],  # paper: Dict[str,str],
            review=kwargs['review'],  # review: List[str],
            decision=kwargs['decision'],  # decision: str,
            model_name=self.model_name,
            rebuttal=kwargs['rebuttal']
            if 'rebuttal' in kwargs
            else None,  # rebuttal: str,
            meta_review=kwargs['meta_review']
            if 'meta_review' in kwargs
            else None,  # meta_review: str,
        )
        self.parsed_output = self.parse(raw_output)
        # Store the input kwargs in parsed_output
        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output: str) -> ReviewEvalOutput:
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

        return ReviewEvalOutput(
            overall_score=overall_score, dimension_scores=dimension_scores
        )
