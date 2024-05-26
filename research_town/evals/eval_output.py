from pydantic import BaseModel, Field, validator

from typing import Optional, Tuple, List
# define output format and output parser

# Output format. Refer to: https://github.com/sotopia-lab/sotopia/blob/2227503f5091961041ddb1da5b7c7836febfa650/sotopia/envs/evaluators.py#L20 .

class EvalOutput_GeneralQuality:
    def __init__(self) -> None:
        self.idea = None
        self.paper = None
        self.reviw = None
        self.disc = None
def parser_GeneralQuality_idea(idea_output:List[str])->List[Tuple(float,str)]:
    pass
