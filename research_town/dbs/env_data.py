import uuid
from typing import Optional

from pydantic import BaseModel, Field


class AgentPaperReviewLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    review_score: Optional[int] = Field(default=0)
    review_content: Optional[str] = Field(default=None)


class AgentPaperRebuttalLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    rebuttal_content: Optional[str] = Field(default=None)


class AgentPaperMetaReviewLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    decision: Optional[bool] = Field(default=False)
    meta_review: Optional[str] = Field(default=None)


class AgentAgentDiscussionLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    agent_from_pk: str
    agent_from_name: str
    agent_to_pk: str
    agent_to_name: str
    message: Optional[str] = Field(default=None)
