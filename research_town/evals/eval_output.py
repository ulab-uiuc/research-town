import re
from typing import List

# define output format and output parser

# Output format. Refer to: https://github.com/sotopia-lab/sotopia/blob/2227503f5091961041ddb1da5b7c7836febfa650/sotopia/envs/evaluators.py#L20 .

class EvalOutput_GeneralQuality:
    def __init__(self) -> None:
        self.idea: List[int] = []
        self.paper: List[int] = []
        self.reviw: List[int] = []

    def parser_GeneralQuality_idea(self,idea_output:List[str])->List[int]:
        # idea_output format: a list of string like "Overall Score=89. Dimension Scores=[8,9,9,9,9,9,9,9,9,9]"
        default_score = int(-1)
        overall_scores = []
        for output in idea_output:
            match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", output, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                overall_scores.append(score)
            else:
                overall_scores.append(default_score)
        self.idea = overall_scores
        return self.idea

    def parser_GeneralQuality_paper(self,paper_output:List[str])->List[int]:
            # paper_output format: a list of string like "Overall Score=89. Dimension Scores=[8,9,9,9,9,9,9,9,9,9]"
        default_score = int(-1)
        overall_scores = []
        for output in paper_output:
            match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", output, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                overall_scores.append(score)
            else:
                overall_scores.append(default_score)
        self.paper = overall_scores
        return self.paper
