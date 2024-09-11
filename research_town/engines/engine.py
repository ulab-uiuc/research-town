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
            ('start', True, 'proposal_writing'),
            ('proposal_writing', True, 'review_writing'),
            ('review_writing', True, 'end'),
            ('review_writing', False, 'start'),
        ]
        for from_env, pass_or_fail, to_env in transitions:
            self.add_transition(from_env, pass_or_fail, to_env)

    def set_transition_funcs(self) -> None:
        transition_funcs: Dict[Tuple[str, str], Callable[..., Any]] = {
            ('start', 'proposal_writing'): self.from_start_to_proposal_writing,
            (
                'proposal_writing',
                'review_writing',
            ): self.from_proposal_writing_to_review_writing,
            ('review_writing', 'end'): self.from_review_writing_to_end,
        }
        for (from_env, to_env), func in transition_funcs.items():
            self.add_transition_func(from_env, func, to_env)

    def from_start_to_proposal_writing(
        self,
        env: StartEnv,
    ) -> Dict[str, Any]:
        member_num = self.config.param.member_num
        leader = env.leader.profile
        members = self.find_members(leader, member_num)
        return {
            'agent_profiles': [leader] + members,
            'agent_roles': ['leader'] + ['member'] * member_num,
            'agent_models': [self.model_name] * (member_num + 1),
        }

    def from_proposal_writing_to_review_writing(
        self,
        env: ProposalWritingEnv,
    ) -> Dict[str, Any]:
        reviewer_num = self.config.param.reviewer_num
        leader = env.leader.profile
        reviewers = self.find_reviewers(env.proposal, reviewer_num)
        chair = self.find_chair(env.proposal)
        return {
            'agent_profiles': [leader] + reviewers + [chair],
            'agent_roles': ['leader'] + ['reviewer'] * reviewer_num + ['chair'],
            'agent_models': [self.model_name] * (reviewer_num + 2),
            'paper': env.proposal,
        }

    def from_review_writing_to_end(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {'meta_review': env.meta_review}
