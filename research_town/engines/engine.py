from ..envs import EndEnv, ProposalWritingEnv, ReviewWritingEnv, StartEnv
from .engine_base import BaseEngine


class Engine(BaseEngine):
    def set_envs(self) -> None:
        env_classes = [StartEnv, ProposalWritingEnv, ReviewWritingEnv, EndEnv]
        self.add_envs([cls(name, self.log_db, self.progress_db, self.paper_db, self.profile_db, self.config)
                       for name, cls in zip(['start', 'proposal_writing', 'review_writing', 'end'], env_classes)])

    def set_transitions(self) -> None:
        transitions = [
            ('start', 'start_proposal', 'proposal_writing'),
            ('proposal_writing', 'start_review', 'review_writing'),
            ('review_writing', 'proposal_accept', 'end'),
            ('review_writing', 'proposal_reject', 'start'),
            ('review_writing', 'parse_error', 'review_writing'),
        ]
        self.add_transitions(transitions)