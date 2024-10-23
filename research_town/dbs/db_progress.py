from ..configs import DatabaseConfig
from ..data.data import Idea, Insight, MetaReview, Proposal, Rebuttal, Review
from .db_complex import ComplexDB


class ProgressDB(ComplexDB):
    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__(
            classes_to_register=[
                Insight,
                Idea,
                Proposal,
                Review,
                Rebuttal,
                MetaReview,
            ],
            config=config,
        )
