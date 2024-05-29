
import re
from typing import Any, Dict

from ..utils.eval_prompter import (
    idea_quality_eval_prompting,
    paper_quality_eval_prompting,
)
from ..utils.decorator import retry_eval
from .output_format import IdeaEvalOutput, PaperEvalOutput, OutputFormatError


class IdeaQualityEvaluator(object):
    def __init__(self,
        model_name: str,
        *args: Any,
        **kwargs: Any
    )-> None:
        self.model_name = model_name
        self.parsed_output = IdeaEvalOutput()

    @retry_eval(output_format=IdeaEvalOutput, retries=5, base_wait_time=1)
    def eval(
        self,
        *args: Any,
        **kwargs: Any,
    )-> IdeaEvalOutput:
        raw_output = idea_quality_eval_prompting(
            idea=kwargs['idea'],
            trend=kwargs['trend'],
            model_name=self.model_name
        )
        self.parsed_output = self.parse(raw_output)
        # check parsed_output
        if not (0 <= self.parsed_output.overall_score <= 100):
            raise OutputFormatError(f"overall score of idea should be an Int between 0 and 100, but it's {self.parsed_output.overall_score}")
        # get pk
        # self.parsed_output.pk = kwargs.get("pk")
        # Store the input kwargs in parsed_output
        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output:str) -> IdeaEvalOutput:
        match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", raw_output, re.IGNORECASE)
        if match:
            return IdeaEvalOutput(overall_score=int(match.group(1)))
        else:
            return IdeaEvalOutput()


class PaperQualityEvaluator(object):
    def __init__(self,
        model_name: str,
        *args: Any,
        **kwargs: Any
    )-> None:
        self.model_name = model_name
        self.parsed_output = PaperEvalOutput()

    @retry_eval(output_format=PaperEvalOutput, retries=5, base_wait_time=1)
    def eval(
        self,
        *args: Any,
        **kwargs: Any,
    )-> PaperEvalOutput:
        raw_output = paper_quality_eval_prompting(
            idea=kwargs['idea'],
            paper=kwargs['paper'],
            model_name=self.model_name
        )
        self.parsed_output = self.parse(raw_output)

        if not (0 <= self.parsed_output.overall_score <= 100):
            raise OutputFormatError(f"overall score of idea should be an Int between 0 and 100, but it's {self.parsed_output.overall_score}")

        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output:str) -> PaperEvalOutput:
        match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", raw_output, re.IGNORECASE)
        if match:
            return PaperEvalOutput(overall_score=int(match.group(1)))
        else:
            return PaperEvalOutput()
