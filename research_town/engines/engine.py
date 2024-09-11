from typing import Any, Dict

from ..envs import EndEnv, ProposalWritingEnv, ReviewWritingEnv, StartEnv
from .engine_base import BaseEngine


class Engine(BaseEngine):
    def set_envs(self) -> None:
        self.add_envs(
            StartEnv(
                'start', self.env_db, self.progress_db, self.paper_db, self.config
            ),
            ProposalWritingEnv(
                'proposal_writing',
                self.env_db,
                self.progress_db,
                self.paper_db,
                self.config,
            ),
            ReviewWritingEnv(
                'review_writing',
                self.env_db,
                self.progress_db,
                self.paper_db,
                self.config,
            ),
            EndEnv('end', self.env_db, self.progress_db, self.paper_db, self.config),
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
        member_num = self.config.param.member_num
        leader = env.leader.profile
        members = self.agent_db.invite_members(leader, member_num)
        return {
            'agent_profiles': [leader] + members,
            'agent_roles': ['leader'] + ['member'] * member_num,
            'agent_models': [self.model_name] * (member_num + 1),
        }

    def start_review(
        self,
        env: ProposalWritingEnv,
    ) -> Dict[str, Any]:
        reviewer_num = self.config.param.reviewer_num
        leader = env.leader.profile
        reviewers = self.agent_db.invite_reviewers(env.proposal, reviewer_num)
        chair = self.agent_db.invite_chairs(env.proposal, chair_num=1)[0]
        return {
            'agent_profiles': [leader] + reviewers + [chair],
            'agent_roles': ['leader'] + ['reviewer'] * reviewer_num + ['chair'],
            'agent_models': [self.model_name] * (reviewer_num + 2),
            'paper': env.proposal,
        }

    def proposal_accept(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {'meta_review': env.meta_review}

    def proposal_reject(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {}

    def parse_error(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {}
