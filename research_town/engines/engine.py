from typing import Any, Dict

from ..envs import EndEnv, ProposalWritingEnv, ReviewWritingEnv, StartEnv
from .engine_base import BaseEngine


class Engine(BaseEngine):
    def set_envs(self) -> None:
        self.add_envs(
            [
                StartEnv(
                    'start',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.profile_db,
                    self.config,
                ),
                ProposalWritingEnv(
                    'proposal_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.profile_db,
                    self.config,
                ),
                ReviewWritingEnv(
                    'review_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.profile_db,
                    self.config,
                ),
                EndEnv(
                    'end',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.profile_db,
                    self.config,
                ),
            ]
        )

    def set_transitions(self) -> None:
        self.add_transitions(
            [
                ('start', 'start_proposal', 'proposal_writing'),
                ('proposal_writing', 'start_review', 'review_writing'),
                ('review_writing', 'proposal_accept', 'end'),
                ('review_writing', 'proposal_reject', 'start'),
                ('review_writing', 'parse_error', 'review_writing'),
            ]
        )