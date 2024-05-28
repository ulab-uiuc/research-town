
from typing import List
from pydantic import BaseModel, Field, Extra


class IdeaEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default=None)
    class Config:
        extra = Extra.allow  # Allows extra fields to be stored

class PaperEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default=None)
    class Config:
        extra = Extra.allow  # Allows extra fields to be stored
