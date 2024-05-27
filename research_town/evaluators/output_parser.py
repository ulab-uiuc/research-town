import re
from typing import List

# define output format and output parser

# Output format. Refer to: https://github.com/sotopia-lab/sotopia/blob/2227503f5091961041ddb1da5b7c7836febfa650/sotopia/envs/evaluators.py#L20 .

class EvalOutputParser(object):
    def __init__(self) -> None:
        self.idea_score: List[int] = []
        self.paper_score: List[int] = []
        self.reviw_score: List[int] = []

    def parse_idea_score(self,idea_output:List[str])->List[int]:
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
        self.idea_score = overall_scores
        return self.idea_score

    def parse_paper_score(self,paper_output:List[str])->List[int]:
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
        self.paper_score = overall_scores
        return self.paper_score
