from typing import Optional
class PaperProfile(object):
    paper_id: str
    title: Optional[str] = None
    abstract: Optional[str] = None

class AgentProfile(object):
    agent_id: str
    name: Optional[str] = None
    profile: Optional[str] = None