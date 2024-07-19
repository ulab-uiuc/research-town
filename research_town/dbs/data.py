import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseDBData(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AgentProfile(BaseDBData):
    name: str
    bio: str
    project_name: Optional[str] = Field(default=None)
    collaborators: Optional[List[str]] = Field(default=[])
    institute: Optional[str] = Field(default=None)
    embed: Optional[Any] = Field(default=None)
    is_proj_leader_candidate: Optional[bool] = Field(default=True)
    is_proj_participant_candidate: Optional[bool] = Field(default=True)
    is_reviewer_candidate: Optional[bool] = Field(default=True)
    is_chair_candidate: Optional[bool] = Field(default=True)


class PaperProfile(BaseDBData):
    authors: List[str] = Field(default=[])
    title: str
    abstract: str
    project_name: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    timestamp: Optional[int] = Field(default=None)
    section_contents: Optional[Dict[str, str]] = Field(default=None)
    table_captions: Optional[Dict[str, str]] = Field(default=None)
    figure_captions: Optional[Dict[str, str]] = Field(default=None)
    bibliography: Optional[Dict[str, str]] = Field(default=None)
    keywords: Optional[List[str]] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    references: Optional[List[Dict[str, str]]] = Field(default=None)
    citation_count: Optional[int] = Field(default=0)
    award: Optional[str] = Field(default=None)
    embed: Optional[Any] = Field(default=None)


class AgentPaperLiteratureReviewLog(BaseDBData):
    timestep: int = Field(default=0)
    paper_pks: List[str]
    agent_pk: str
    project_name: Optional[str] = Field(default=None)
    insight_pks: Optional[List[str]] = Field(default=[])
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentIdeaBrainstormingLog(BaseDBData):
    timestep: int = Field(default=0)
    idea_pk: str
    agent_pk: str
    project_name: Optional[str] = Field(default=None)
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentAgentCollaborationFindingLog(BaseDBData):
    timestep: int = Field(default=0)
    agent_pk: str
    project_name: Optional[str] = Field(default=None)
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentAgentIdeaDiscussionLog(BaseDBData):
    timestep: int = Field(default=0)
    agent_from_pk: str
    agent_from_name: str
    agent_to_pk: str
    agent_to_name: str
    project_name: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)


class AgentPaperWritingLog(BaseDBData):
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    project_name: Optional[str] = Field(default=None)
    other_agent_pks: Optional[List[str]] = Field(default=[])


class AgentPaperReviewWritingLog(BaseDBData):
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    project_name: Optional[str] = Field(default=None)
    other_agent_pks: Optional[List[str]] = Field(default=[])
    score: Optional[int] = Field(default=0)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)


class AgentPaperRebuttalWritingLog(BaseDBData):
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    project_name: Optional[str] = Field(default=None)
    other_agent_pks: Optional[List[str]] = Field(default=[])
    rebuttal_content: Optional[str] = Field(default=None)


class AgentPaperMetaReviewWritingLog(BaseDBData):
    timestep: int = Field(default=0)
    paper_pk: str
    agent_pk: str
    project_name: Optional[str] = Field(default=None)
    other_agent_pks: Optional[List[str]] = Field(default=[])
    decision: Optional[bool] = Field(default=False)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)


class ResearchInsight(BaseDBData):
    project_name: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    eval_score: Optional[List[int]] = Field(default=[])  # evaluation scores
    model_config = ConfigDict(extra='allow')


class ResearchIdea(BaseDBData):
    project_name: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    eval_score: Optional[List[int]] = Field(default=[])  # evaluation scores
    model_config = ConfigDict(extra='allow')


class ResearchPaperSubmission(BaseDBData):
    project_name: Optional[str] = Field(default=None)
    abstract: str
    title: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    conference: Optional[str] = Field(default=None)
    eval_score: Optional[List[int]] = Field(default=[])  # evaluation scores
    model_config = ConfigDict(extra='allow')


class ResearchReview(BaseDBData):
    project_name: Optional[str] = Field(default=None)
    paper_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    score: Optional[int] = Field(default=None)
    eval_score: Optional[List[int]] = Field(default=[])  # evaluation scores
    model_config = ConfigDict(extra='allow')


class ResearchRebuttal(BaseDBData):
    project_name: Optional[str] = Field(default=None)
    paper_pk: Optional[str] = Field(default=None)
    reviewer_pk: Optional[str] = Field(default=None)
    author_pk: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    eval_score: Optional[List[int]] = Field(default=[])  # evaluation scores
    model_config = ConfigDict(extra='allow')


class ResearchMetaReview(BaseDBData):
    project_name: Optional[str] = Field(default=None)
    paper_pk: Optional[str] = Field(default=None)
    chair_pk: Optional[str] = Field(default=None)
    reviewer_pks: List[str] = Field(default=[])
    author_pk: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    weakness: Optional[str] = Field(default=None)
    decision: bool = Field(default=False)
    eval_score: Optional[List[int]] = Field(default=[])  # evaluation scores
    model_config = ConfigDict(extra='allow')
