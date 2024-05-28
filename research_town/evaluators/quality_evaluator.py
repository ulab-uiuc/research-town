
from typing import Any, Dict, List, Optional

from ..utils.eval_prompter import (
    idea_quality_eval_prompting,
    paper_quality_eval_prompting,
)
from .output_format import EvalOutputParser


class QualityEvaluator(object):
    def __init__(self,
        model_name: str,
        parser: Optional[EvalOutputParser] = EvalOutputParser(),
        *args: Any,
        **kwargs: Any
    )-> None:
        self.model_name = model_name
        self.parser = parser

    def __call__():
        return

    def eval(
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

    def parse(self, raw_output:str) -> IdeaEvalOutput:
        match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", raw_output, re.IGNORECASE)
        if match:
            return PaperEvalOutput(overall_score=int(match.group(1)))
        else:
            return PaperEvalOutput()

