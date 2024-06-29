import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    collaborators: Optional[List[str]] = Field(default=[])
    institute: Optional[str] = Field(default=None)
