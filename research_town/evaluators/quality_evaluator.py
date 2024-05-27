
from typing import Any, Dict, List, Tuple, Union

from ..utils.eval_prompter import (
    idea_quality_eval_prompting,
    paper_quality_eval_prompting,
)
from .output_parser import EvalOutputParser


class QualityEvaluator(object):
    def __init__(self,
        model_name: str,
        progress_dict: Dict[str, Union[Dict[str, str], Dict[str, Tuple[str, str]]]],
        *args: Any,
        **kwargs: Any
    )-> None:
        self.model_name = model_name
        self.prompt = ""
        # progress with info in a dict to evaluate
        # keys: 1) idea; 2) paper; 3) review; 4) discussion.
        required_keys = ['idea', 'paper', 'review', 'discussion','trend']
        for key in required_keys:
            if key not in progress_dict:
                raise ValueError(f"Missing required key in progress dic: {key}")
        self.progress2eval = {key: progress_dict[key] for key in required_keys}
        self.parser = EvalOutputParser() # to store the result of evaluation


    def eval_idea(self)-> List[int]:
        # generate the prompt template and prompting (prompter in eval_prompter.py)
        model_output = idea_quality_eval_prompting(
            ideas=self.progress2eval['idea'],
            trends=self.progress2eval['trend'],
            model_name=self.model_name
        )
        # parse the prompting output(parser in eval_out.py). Extract a score in List[int]. Tuple(overall score, soundness, insightful, novelty, practial..)
        parsed_idea_eval = self.parser.parse_idea_score(
            idea_output=model_output
        )
        return parsed_idea_eval

    def eval_paper(self)-> List[int]:
        model_output = paper_quality_eval_prompting(
            ideas=self.progress2eval['idea'],
            papers=self.progress2eval['paper'],
            model_name=self.model_name
        )
        # parse the prompting output(parser in eval_out.py). Extract a score in List[int]. Tuple(overall score, soundness, insightful, novelty, practial..)
        parsed_paper_eval = self.parser.parse_paper_score(paper_output=model_output)
        return parsed_paper_eval

    def eval_review(self)-> None:
        # component/stage evaluation: compare with open review by ranking consistency
        pass
