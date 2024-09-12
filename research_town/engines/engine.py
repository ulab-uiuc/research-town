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
                    self.agent_db,
                    self.config,
                ),
                ProposalWritingEnv(
                    'proposal_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.agent_db,
                    self.config,
                ),
                ReviewWritingEnv(
                    'review_writing',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.agent_db,
                    self.config,
                ),
                EndEnv(
                    'end',
                    self.log_db,
                    self.progress_db,
                    self.paper_db,
                    self.agent_db,
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

    def set_transition_funcs(self) -> None:
        self.add_transition_funcs(
            [
                ('start', self.start_proposal, 'proposal_writing'),
                ('proposal_writing', self.start_review, 'review_writing'),
                ('review_writing', self.proposal_accept, 'end'),
                ('review_writing', self.proposal_reject, 'start'),
                ('review_writing', self.parse_error, 'review_writing'),
            ]
        )

    def start_proposal(
        self,
        env: StartEnv,
    ) -> Dict[str, Any]:
        return {'leader_profile': env.leader.profile}

    def start_review(
        self,
        env: ProposalWritingEnv,
    ) -> Dict[str, Any]:
        return {'proposal': env.proposal, 'leader_profile': env.leader.profile}

    def proposal_accept(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {'meta_review': env.meta_review}

    def proposal_reject(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {}

    def parse_error(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {}
