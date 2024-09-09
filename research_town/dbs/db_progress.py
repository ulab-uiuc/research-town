from typing import Optional

from .data import (
    Experiment,
    Idea,
    Insight,
    MetaReview,
    Proposal,
    ResearchRebuttal,
    Review,
)
from .db_complex import ComplexDB


class ProgressDB(ComplexDB):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(
            classes_to_register=[
                Insight,
                Idea,
                Proposal,
                Review,
                ResearchRebuttal,
                MetaReview,
                Experiment,
            ],
            load_file_path=load_file_path,
        )
