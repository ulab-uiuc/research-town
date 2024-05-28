
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

# add OutputFormat Error for the capture of retry decorator "exponential_backoff"
class OutputFormatError(Exception):
    pass