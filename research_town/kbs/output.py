from typing import Optional

class ResearchOutput(object):
    output_id: str
    paper_id: Optional[str] = None
    trend: Optional[str] = None
    idea: Optional[str] = None
    domain: Optional[str] = None
