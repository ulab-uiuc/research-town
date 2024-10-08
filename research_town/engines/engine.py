from ..envs import (
    EndEnv,
    ProposalWritingwithoutRAGEnv,
    ProposalWritingwithRAGEnv,
    ReviewWritingEnv,
    StartEnv,
)
from .engine_base import BaseEngine


class Engine(BaseEngine):
    def set_envs(self) -> None:
        if self.config.param.use_rag:
            envs = [
                StartEnv('start', self.config, self.agent_manager),
                ProposalWritingwithRAGEnv(
                    'proposal_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.config,
                    self.agent_manager,
                ),
                ReviewWritingEnv(
                    'review_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.config,
                    self.agent_manager,
                ),
                EndEnv('end', self.config, self.agent_manager),
            ]
        else:
            envs = [
                StartEnv('start', self.config, self.agent_manager),
                ProposalWritingwithoutRAGEnv(
                    'proposal_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.config,
                    self.agent_manager,
                ),
                ReviewWritingEnv(
                    'review_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.config,
                    self.agent_manager,
                ),
                EndEnv('end', self.config, self.agent_manager),
            ]
        self.add_envs(envs)

    def set_transitions(self) -> None:
        transitions = [
            ('start', 'start_proposal', 'proposal_writing'),
            ('proposal_writing', 'start_review', 'review_writing'),
            ('proposal_writing', 'error', 'end'),
            ('review_writing', 'proposal_accept', 'end'),
            ('review_writing', 'proposal_reject', 'start'),
            ('review_writing', 'parse_error', 'review_writing'),
            ('review_writing', 'error', 'end'),
        ]
        self.add_transitions(transitions)
