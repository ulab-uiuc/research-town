from .data import (
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReviewForPaperSubmission,
    ResearchPaperSubmission,
    ResearchRebuttalForPaperSubmission,
    ResearchReviewForPaperSubmission,
)
from .db_complex import ComplexDB


class ProgressDB(ComplexDB):
    def __init__(self) -> None:
        super().__init__()
        for data_class in [
            ResearchInsight,
            ResearchIdea,
            ResearchPaperSubmission,
            ResearchReviewForPaperSubmission,
            ResearchRebuttalForPaperSubmission,
            ResearchMetaReviewForPaperSubmission,
        ]:
            self.register_class(data_class)
