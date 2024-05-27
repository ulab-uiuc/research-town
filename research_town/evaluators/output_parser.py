import re
from typing import List
from pydantic import BaseModel, Field


class IdeaEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)

class PaperEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)

class EvalOutputParser(object):
    def parse_idea_score(self, raw_output:str) -> IdeaEvalOutput:
        match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", raw_output, re.IGNORECASE)
        if match:
            return PaperEvalOutput(overall_score=int(match.group(1)))
        else:
            return PaperEvalOutput()

    def parse_paper_score(self, raw_output:str) -> PaperEvalOutput:
        match = re.search(r"Overall\s*Score\s*\W*(\d+)\W*", raw_output, re.IGNORECASE)
        if match:
            return PaperEvalOutput(overall_score=int(match.group(1)))
        else:
            return PaperEvalOutput()
