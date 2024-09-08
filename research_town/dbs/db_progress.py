from typing import Optional

from .data import (
    ResearchIdea,
    ResearchInsight,
    ResearchMetaReview,
    ResearchProposal,
    ResearchRebuttal,
    ResearchReview,
)
from .db_complex import ComplexDB


class ProgressDB(ComplexDB):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(
            classes_to_register=[
                ResearchInsight,
                ResearchIdea,
                ResearchProposal,
                ResearchReview,
                ResearchRebuttal,
                ResearchMetaReview,
            ],
            load_file_path=load_file_path,
        )
