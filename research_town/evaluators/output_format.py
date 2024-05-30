
from beartype.typing import Type, TypeVar

from pydantic import BaseModel, Extra, Field, validator

T = TypeVar('T', bound=BaseModel)

class IdeaEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default='0')
    class Config:
        extra = Extra.allow  # Allows extra fields to be stored

    @validator('overall_score')
    def validate_overall_score(cls: Type[T], v: int) -> int:
        if v is None:
            raise ValueError("Overall score cannot be None")
        if not (0 <= v <= 100):
            raise ValueError("Overall score must be between 0 and 100")
        return v


class PaperEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default='0')
    class Config:
        extra = Extra.allow  # Allows extra fields to be stored

    @validator('overall_score')
    def validate_overall_score(cls: Type[T], v: int) -> int:
        if v is None:
            raise ValueError("Overall score cannot be None")
        if not (0 <= v <= 100):
            raise ValueError("Overall score must be between 0 and 100")
        return v

class OutputFormatError(Exception):
    def __init__(self, message:str="Output format error")-> None:
        self.message = message
        super().__init__(self.message)
