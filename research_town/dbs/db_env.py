from .data import (
    AgentAgentCollaborationFindingLog,
    AgentAgentIdeaDiscussionLog,
    AgentIdeaBrainstormingLog,
    AgentPaperLiteratureReviewLog,
    AgentPaperMetaReviewWritingLog,
    AgentPaperRebuttalWritingLog,
    AgentPaperReviewWritingLog,
    AgentPaperWritingLog,
)
from .db_complex import ComplexDB


class EnvLogDB(ComplexDB):
    def __init__(self) -> None:
        super().__init__()
        for data_class in [
            AgentPaperLiteratureReviewLog,
            AgentIdeaBrainstormingLog,
            AgentAgentCollaborationFindingLog,
            AgentAgentIdeaDiscussionLog,
            AgentPaperWritingLog,
            AgentPaperReviewWritingLog,
            AgentPaperRebuttalWritingLog,
            AgentPaperMetaReviewWritingLog,
        ]:
            self.register_class(data_class)
