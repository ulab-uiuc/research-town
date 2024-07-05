import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

class AgentPaperLiteratureReviewLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    insight_pks: Optional[List[str]] = Field(default=[])
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentIdeaBrainstormingLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    idea_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentAgentCollaborationFindingLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentAgentIdeaDiscussionLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    agent_from_pk: str
    agent_from_name: str
    agent_to_pk: str
    agent_to_name: str
    message: Optional[str] = Field(default=None)


class AgentPaperWritingLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentPaperReviewWritingLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])
    review_score: Optional[int] = Field(default=0)
    review_content: Optional[str] = Field(default=None)


class AgentPaperRebuttalWritingLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])
    rebuttal_content: Optional[str] = Field(default=None)


class AgentPaperMetaReviewWritingLog(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])
    decision: Optional[bool] = Field(default=False)
    meta_review: Optional[str] = Field(default=None)
