import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseEnvLogData(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestep: int = Field(default=0)
    model_config = ConfigDict(
        extra='allow',
    )


class AgentPaperLiteratureReviewLog(BaseEnvLogData):
    paper_pks: List[str]
    agent_pk: str
    insight_pks: Optional[List[str]] = Field(default=[])
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentIdeaBrainstormingLog(BaseEnvLogData):
    idea_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentAgentCollaborationFindingLog(BaseEnvLogData):
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentAgentIdeaDiscussionLog(BaseEnvLogData):
    agent_from_pk: str
    agent_from_name: str
    agent_to_pk: str
    agent_to_name: str
    message: Optional[str] = Field(default=None)


class AgentPaperWritingLog(BaseEnvLogData):
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentPaperReviewWritingLog(BaseEnvLogData):
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])
    score: Optional[int] = Field(default=0)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)


class AgentPaperRebuttalWritingLog(BaseEnvLogData):
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])
    rebuttal_content: Optional[str] = Field(default=None)


class AgentPaperMetaReviewWritingLog(BaseEnvLogData):
    paper_pk: str
    agent_pk: str
    other_agent_pks: Optional[List[str]] = Field(default=[])
    decision: Optional[bool] = Field(default=False)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
