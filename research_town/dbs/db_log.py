from ..configs import DatabaseConfig
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
    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__(
            classes_to_register=[
                LiteratureReviewLog,
                IdeaBrainstormLog,
                ProposalWritingLog,
                ReviewWritingLog,
                RebuttalWritingLog,
                MetaReviewWritingLog,
            ],
            config=config,
        )
