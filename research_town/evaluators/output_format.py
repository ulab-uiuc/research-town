
from pydantic import BaseModel, Extra, Field


class IdeaEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default='0')
    class Config:
        extra = Extra.allow  # Allows extra fields to be stored

class PaperEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default='0')
    class Config:
        extra = Extra.allow  # Allows extra fields to be stored
