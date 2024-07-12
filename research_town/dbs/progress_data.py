import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseProgressData(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_config = ConfigDict(
        extra='allow',
    )


class ResearchInsight(BaseProgressData):
    content: Optional[str] = Field(default=None)


class ResearchIdea(BaseProgressData):
    content: Optional[str] = Field(default=None)


class ResearchPaperSubmission(BaseProgressData):
    title: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    conference: Optional[str] = Field(default=None)


class ResearchReviewForPaperSubmission(BaseProgressData):
    paper_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    score: Optional[int] = Field(default=None)


class ResearchRebuttalForPaperSubmission(BaseProgressData):
    paper_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    author_pk: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)


class ResearchMetaReviewForPaperSubmission(BaseProgressData):
    paper_pk: Optional[str] = Field(default=None)
    chair_pk: Optional[str] = Field(default=None)
    reviewer_pks: List[str] = Field(default=[])
    author_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    decision: bool = Field(default=False)
