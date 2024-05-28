import re
from typing import List
from pydantic import BaseModel, Field


class IdeaEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default=None)

class PaperEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
