from beartype.typing import List, Type, TypeVar
from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar('T', bound=BaseModel)


class IdeaEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default='0')
    dimension_scores: List[int] = Field(default=[])

    model_config = ConfigDict(extra='allow')

    @field_validator('overall_score')
    def validate_overall_score(cls: Type[T], v: int) -> int:
        if v is None:
            raise ValueError('Overall score cannot be None')
        if not (0 <= v <= 100):
            raise ValueError('Overall score must be between 0 and 100')
        return v

    @field_validator('dimension_scores')
    def validate_dimension_scores(cls, v: List[int]) -> List[int]:
        for score in v:
            if not (0 <= score <= 10):
                raise ValueError('Each dimension score must be between 0 and 10')
        return v


class PaperEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default='0')
    dimension_scores: List[int] = Field(default=[])

    model_config = ConfigDict(extra='allow')

    @field_validator('overall_score')
    def validate_overall_score(cls: Type[T], v: int) -> int:
        if v is None:
            raise ValueError('Overall score cannot be None')
        if not (0 <= v <= 100):
            raise ValueError('Overall score must be between 0 and 100')
        return v

    @field_validator('dimension_scores')
    def validate_dimension_scores(cls, v: List[int]) -> List[int]:
        for score in v:
            if not (0 <= score <= 10):
                raise ValueError('Each dimension score must be between 0 and 10')
        return v


class ReviewEvalOutput(BaseModel):
    overall_score: int = Field(default=-1)
    pk: str = Field(default='0')
    dimension_scores: List[int] = Field(default=[])

    model_config = ConfigDict(extra='allow')

    @field_validator('overall_score')
    def validate_overall_score(cls: Type[T], v: int) -> int:
        if v is None:
            raise ValueError('Overall score cannot be None')
        if not (0 <= v <= 100):
            raise ValueError('Overall score must be between 0 and 100')
        return v

    @field_validator('dimension_scores')
    def validate_dimension_scores(cls, v: List[int]) -> List[int]:
        for score in v:
            if not (0 <= score <= 10):
                raise ValueError('Each dimension score must be between 0 and 10')
        return v


class OutputFormatError(Exception):
    def __init__(self, message: str = 'Output format error') -> None:
        self.message = message
        super().__init__(self.message)
