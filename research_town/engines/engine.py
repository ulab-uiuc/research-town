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
            ('proposal_writing', 'review_writing'): self.from_proposal_writing_to_review_writing,
            ('review_writing', 'end'): self.from_review_writing_to_end,
        }
        for (from_env, to_env), func in transition_funcs.items():
            self.add_transition_func(from_env, func, to_env)


    def from_start_to_proposal_writing(
        self,
        env: StartEnv,
    ) -> Dict[str, Any]:
        proj_participant_num = self.config.param.proj_participant_num
        proj_leader = env.proj_leader.profile
        proj_participants = self.find_proj_participants(
            proj_leader, proj_participant_num
        )
        return {
            'agent_profiles': [proj_leader] + proj_participants,
            'agent_roles': ['proj_leader']
            + ['proj_participant'] * proj_participant_num,
            'agent_models': ['gpt-4o'] * (proj_participant_num + 1),
        }

    def from_proposal_writing_to_review_writing(
        self,
        env: ProposalWritingEnv,
    ) -> Dict[str, Any]:
        reviewer_num = self.config.param.reviewer_num
        proj_leader = env.proj_leader.profile
        reviewers = self.find_reviewers(env.paper, reviewer_num)
        chair = self.find_chair(env.paper)
        return {
            'agent_profiles': [proj_leader] + reviewers + [chair],
            'agent_roles': ['proj_leader'] + ['reviewer'] * reviewer_num + ['chair'],
            'agent_models': ['gpt-4o'] * (reviewer_num + 2),
            'paper': env.paper,
        }

    def from_review_writing_to_end(self, env: ReviewWritingEnv) -> Dict[str, Any]:
        return {'reviews': env.reviews}
