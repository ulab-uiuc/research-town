
from typing import Any, Dict, List, Optional

from ..utils.eval_prompter import (
    idea_quality_eval_prompting,
    paper_quality_eval_prompting,
)
from .output_parser import EvalOutputParser


class QualityEvaluator(object):
    def __init__(self,
        model_name: str,
        parser: Optional[EvalOutputParser] = EvalOutputParser(),
        *args: Any,
        **kwargs: Any
    )-> None:
        self.model_name = model_name
        self.parser = parser

    def eval_idea(
        self, 
        idea: Dict[str], 
        trend: Dict[str], 
        *args, 
        **kwargs
    )-> List[int]:
        raw_output = idea_quality_eval_prompting(
            ideas=idea,
            trends=trend,
            model_name=self.model_name
        )
        parsed_output = self.parser.parse_idea_score(raw_output)
        return parsed_output

    def eval_paper(
        self, 
        idea: Dict[str], 
        paper: Dict[str, str]
    )-> List[int]:
        raw_output = paper_quality_eval_prompting(
            ideas=idea,
            papers=paper,
            model_name=self.model_name
        )
        parsed_output = self.parser.parse_paper_score(raw_output)
        return parsed_output

    def eval_review(self)-> None:
        pass
