from typing import Optional

from ..data.data import (
    IdeaBrainstormLog,
    LiteratureReviewLog,
    MetaReviewWritingLog,
    ProposalWritingLog,
    RebuttalWritingLog,
    ReviewWritingLog,
)
from .db_complex import ComplexDB


class LogDB(ComplexDB):
    def __init__(self, load_file_path: Optional[str] = None) -> None:
        super().__init__(
            classes_to_register=[
                LiteratureReviewLog,
                IdeaBrainstormLog,
                ProposalWritingLog,
                ReviewWritingLog,
                RebuttalWritingLog,
                MetaReviewWritingLog,
            ],
            load_file_path=load_file_path,
        )
