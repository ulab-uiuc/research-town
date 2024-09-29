from typing import Optional

from ..data.data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from .db_complex import ComplexDB


class ProgressDB(ComplexDB):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(
            classes_to_register=[
                Insight,
                Idea,
                Proposal,
                Review,
                Rebuttal,
                MetaReview,
            ],
            load_file_path=load_file_path,
        )
