
import re
from typing import Any, Dict

from ..utils.eval_prompter import (
    idea_quality_eval_prompting,
    paper_quality_eval_prompting,
)
from .output_format import IdeaEvalOutput, PaperEvalOutput


class IdeaQualityEvaluator(object):
    def __init__(self,
        model_name: str,
        *args: Any,
        **kwargs: Any
    )-> None:
        self.model_name = model_name
        self.parsed_output = IdeaEvalOutput()


    def eval(
        self,
        idea: str,
        trend: str,
        *args: Any,
        **kwargs: Any,
    )-> IdeaEvalOutput:
        raw_output = idea_quality_eval_prompting(
            idea=idea,
            trend=trend,
            model_name=self.model_name
        )
        self.parsed_output = self.parse(raw_output)
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


    def eval(
        self,
        idea: str,
        paper: Dict[str,str],
        *args: Any,
        **kwargs: Any,
    )-> PaperEvalOutput:
        raw_output = paper_quality_eval_prompting(
            idea=idea,
            paper=paper,
            model_name=self.model_name
        )
        self.parsed_output = self.parse(raw_output)
        # Store the input kwargs in parsed_output
        for key, value in kwargs.items():
            setattr(self.parsed_output, key, value)
        return self.parsed_output

    def parse(self, raw_output:str) -> PaperEvalOutput:
        match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", raw_output, re.IGNORECASE)
        if match:
            return PaperEvalOutput(overall_score=int(match.group(1)))
        else:
            return PaperEvalOutput()
