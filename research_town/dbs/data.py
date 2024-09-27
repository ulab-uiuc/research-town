import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Data(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: Optional[str] = Field(default=None)


class Profile(Data):
    name: str
    bio: str
    collaborators: Optional[List[str]] = Field(default=[])
    domain: Optional[List[str]] = Field(default=[])
    institute: Optional[str] = Field(default=None)
    embed: Optional[Any] = Field(default=None)
    is_leader_candidate: Optional[bool] = Field(default=True)
    is_member_candidate: Optional[bool] = Field(default=True)
    is_reviewer_candidate: Optional[bool] = Field(default=True)
    is_chair_candidate: Optional[bool] = Field(default=True)


class Paper(Data):
    authors: List[str] = Field(default=[])
    title: str
    abstract: str
    url: Optional[str] = Field(default=None)
    timestamp: Optional[int] = Field(default=None)
    sections: Optional[Dict[str, str]] = Field(default=None)
    table_captions: Optional[Dict[str, str]] = Field(default=None)
    figure_captions: Optional[Dict[str, str]] = Field(default=None)
    bibliography: Optional[Dict[str, str]] = Field(default=None)
    keywords: Optional[List[str]] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    references: Optional[List[Dict[str, str]]] = Field(default=None)
    citation_count: Optional[int] = Field(default=0)
    award: Optional[str] = Field(default=None)
    embed: Optional[Any] = Field(default=None)


class Log(Data):
    timestep: int = Field(default=0)
    profile_pk: str


class LiteratureReviewLog(Log):
    insight_pk: Optional[str] = Field(default=None)


class IdeaBrainstormLog(Log):
    idea_pk: str


class ProposalWritingLog(Log):
    proposal_pk: str


class ReviewWritingLog(Log):
    review_pk: str


class RebuttalWritingLog(Log):
    rebuttal_pk: str


class MetaReviewWritingLog(Log):
    metareview_pk: str


class Progress(Data):
    content: str = Field(default='')
    eval_score: Optional[List[int]] = Field(default=[])  # evaluation scores


class Insight(Progress):
    model_config = ConfigDict(extra='allow')


class Idea(Progress):
    model_config = ConfigDict(extra='allow')


class Proposal(Progress):
    q1: Optional[str] = Field(default=None)
    q2: Optional[str] = Field(default=None)
    q3: Optional[str] = Field(default=None)
    q4: Optional[str] = Field(default=None)
    q5: Optional[str] = Field(default=None)
    abstract: str = Field(default='')
    title: Optional[str] = Field(default=None)
    conference: Optional[str] = Field(default=None)
    model_config = ConfigDict(extra='allow')


class Review(Progress):
    proposal_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    ethical_concerns: Optional[str] = Field(default=None)
    score: Optional[int] = Field(default=None)
    model_config = ConfigDict(extra='allow')


class Rebuttal(Progress):
    q1: Optional[str] = Field(default=None)
    q2: Optional[str] = Field(default=None)
    q3: Optional[str] = Field(default=None)
    q4: Optional[str] = Field(default=None)
    q5: Optional[str] = Field(default=None)
    proposal_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    author_pk: Optional[str] = Field(default=None)
    model_config = ConfigDict(extra='allow')


class MetaReview(Progress):
    proposal_pk: Optional[str] = Field(default=None)
    chair_pk: Optional[str] = Field(default=None)
    reviewer_pks: List[str] = Field(default=[])
    author_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    ethical_concerns: Optional[str] = Field(default=None)
    decision: bool = Field(default=False)
    model_config = ConfigDict(extra='allow')
