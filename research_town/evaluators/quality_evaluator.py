import re

from beartype.typing import Any

from ..utils.decorator import parsing_error_exponential_backoff
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
        match = re.search(r'Overall\s*Score\s*\W*(\d+)\W*',
                          raw_output, re.IGNORECASE)
        if match:
            try:
                return IdeaEvalOutput(overall_score=int(match.group(1)))
            except ValueError as e:
                raise OutputFormatError(f'Invalid overall score: {e}')
        else:
            raise OutputFormatError(
                "Output format error: 'Overall Score' not found")


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
            idea=kwargs['idea'], paper=kwargs['paper'], model_name=self.model_name
        )
        self.parsed_output = self.parse(raw_output)

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output: str) -> PaperEvalOutput:
        match = re.search(r'Overall\s*Score\s*\W*(\d+)\W*',
                          raw_output, re.IGNORECASE)
        if match:
            try:
                return PaperEvalOutput(overall_score=int(match.group(1)))
            except ValueError as e:
                raise OutputFormatError(f'Invalid overall score: {e}')
        else:
            raise OutputFormatError(
                "Output format error: 'Overall Score' not found")


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
            review=kwargs['review'],  # review: Dict[str,str],
            decision=kwargs['decision'],  # decision: str,
            model_name=self.model_name,
        )
        self.parsed_output = self.parse(raw_output)
        # Store the input kwargs in parsed_output
        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output: str) -> ReviewEvalOutput:
        match = re.search(r'Overall\s*Score\s*\W*(\d+)\W*',
                          raw_output, re.IGNORECASE)
        if match:
            try:
                return ReviewEvalOutput(overall_score=int(match.group(1)))
            except ValueError as e:
                raise OutputFormatError(f'Invalid overall score: {e}')
        else:
            raise OutputFormatError(
                f"Output format error: 'Overall Score' not found. Raw output is {raw_output}."
            )
