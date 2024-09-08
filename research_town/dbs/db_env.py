from typing import Optional

from .data import (
    AgentAgentCollaborationFindingLog,
    AgentAgentIdeaDiscussionLog,
    AgentExperimentLog,
    AgentIdeaBrainstormingLog,
    AgentPaperLiteratureReviewLog,
    AgentPaperMetaReviewWritingLog,
    AgentPaperRebuttalWritingLog,
    AgentPaperReviewWritingLog,
    AgentPaperWritingLog,
)
from .db_complex import ComplexDB


class EnvLogDB(ComplexDB):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(
            classes_to_register=[
                AgentPaperLiteratureReviewLog,
                AgentIdeaBrainstormingLog,
                AgentAgentCollaborationFindingLog,
                AgentAgentIdeaDiscussionLog,
                AgentPaperWritingLog,
                AgentPaperReviewWritingLog,
                AgentPaperRebuttalWritingLog,
                AgentPaperMetaReviewWritingLog,
                AgentExperimentLog,
            ],
            load_file_path=load_file_path,
        )
