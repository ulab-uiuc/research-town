from typing import Any, Callable, Dict, Tuple

from ..envs import EndEnv, ProposalWritingEnv, ReviewWritingEnv, StartEnv
from .engine_base import BaseEngine


class Engine(BaseEngine):
    def set_envs(self) -> None:
        self.add_env(
            'start',
            StartEnv(self.env_db, self.progress_db, self.paper_db, self.config),
        )
        self.add_env(
            'proposal_writing',
            ProposalWritingEnv(
                self.env_db, self.progress_db, self.paper_db, self.config
            ),
        )
        self.add_env(
            'review_writing',
            ReviewWritingEnv(self.env_db, self.progress_db, self.paper_db, self.config),
        )
        self.add_env(
            'end',
            EndEnv(self.env_db, self.progress_db, self.paper_db, self.config),
        )

    def set_transitions(self) -> None:
        transitions = [
            ('start', 'start_proposal', 'proposal_writing'),
            ('proposal_writing', 'start_review', 'review_writing'),
            ('review_writing', 'proposal_accept', 'end'),
            ('review_writing', 'proposal_reject', 'start'),
            ('review_writing', 'parse_error', 'review_writing'),
        ]
        for from_env, trigger, to_env in transitions:
            self.add_transition(from_env, trigger, to_env)

    def set_transition_funcs(self) -> None:
        transition_funcs: Dict[Tuple[str, str], Callable[..., Any]] = {
            ('start', 'proposal_writing'): self.start_proposal,
            ('proposal_writing', 'review_writing'): self.start_review,
            ('review_writing', 'end'): self.proposal_accept,
        }
        for (from_env, to_env), func in transition_funcs.items():
            self.add_transition_func(from_env, func, to_env)

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
