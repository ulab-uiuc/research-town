import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchInsight(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: Optional[str] = Field(default=None)

    class Config:
        extra = 'allow'


class ResearchIdea(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: Optional[str] = Field(default=None)

    class Config:
        extra = 'allow'


class ResearchPaperSubmission(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    conference: Optional[str] = Field(default=None)

    class Config:
        extra = 'allow'


class ResearchReviewForPaperSubmission(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    paper_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    score: Optional[int] = Field(default=None)

    class Config:
        extra = 'allow'


class ResearchRebuttalForPaperSubmission(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    paper_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    author_pk: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)

    class Config:
        extra = 'allow'


class ResearchMetaReviewForPaperSubmission(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    paper_pk: Optional[str] = Field(default=None)
    area_chair_pk: Optional[str] = Field(default=None)
    reviewer_pks: List[str] = Field(default=[])
    author_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    decision: bool = Field(default=False)

    class Config:
        extra = 'allow'
