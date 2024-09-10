from typing import Any, Callable, Dict, Tuple

from ..envs import EndEnv, ProposalWritingEnv, ReviewWritingEnv, StartEnv
from .engine_base import BaseEngine


class Engine(BaseEngine):
    def set_envs(self) -> None:
        self.add_envs(
            StartEnv('start', self.env_db, self.progress_db, self.paper_db, self.config),
            ProposalWritingEnv('proposal_writing', self.env_db, self.progress_db, self.paper_db, self.config),
            ReviewWritingEnv('review_writing', self.env_db, self.progress_db, self.paper_db, self.config),
            EndEnv('end', self.env_db, self.progress_db, self.paper_db, self.config),
        )

    def set_transitions(self) -> None:
        self.add_transitions([
                ('start', True, 'proposal_writing'),
                ('proposal_writing', True, 'review_writing'),
                ('review_writing', True, 'end'),
                ('review_writing', False, 'start'),
        ])

    def set_transition_funcs(self) -> None:
        self.add_transition_funcs([
            ('start', self.from_start_to_proposal_writing, 'proposal_writing'),
            ('proposal_writing', self.from_proposal_writing_to_review_writing, 'review_writing'),
            ('review_writing', self.from_review_writing_to_end, 'end'),
        ])

    def from_start_to_proposal_writing(
        self,
        env: StartEnv,
    ) -> Dict[str, Any]:
        return {'leader': env.leader}

    def from_proposal_writing_to_review_writing(
        self,
        env: ProposalWritingEnv,
    ) -> Dict[str, Any]:
        return {'leader': env.leader, 'paper': env.proposal}

    def from_review_writing_to_end(
        self, 
        env: ReviewWritingEnv
    ) -> Dict[str, Any]:
        return {'meta_review': env.meta_review}
