from typing import Any, Callable, Dict, Tuple

from ..envs import EndEnv, PaperSubmissionEnv, PeerReviewEnv, StartEnv
from .engine_base import BaseEngine


class LifecycleEngine(BaseEngine):
    def set_envs(self) -> None:
        self.add_env(
            'start',
            StartEnv(self.env_db, self.progress_db, self.paper_db, self.config),
        )
        self.add_env(
            'paper_submission',
            PaperSubmissionEnv(
                self.env_db, self.progress_db, self.paper_db, self.config
            ),
        )
        self.add_env(
            'peer_review',
            PeerReviewEnv(self.env_db, self.progress_db, self.paper_db, self.config),
        )
        self.add_env(
            'end',
            EndEnv(self.env_db, self.progress_db, self.paper_db, self.config),
        )

    def set_transitions(self) -> None:
        transitions = [
            ('start', True, 'paper_submission'),
            ('start', False, 'paper_submission'),
            ('paper_submission', True, 'peer_review'),
            ('paper_submission', False, 'paper_submission'),
            ('peer_review', False, 'peer_review'),
            ('peer_review', True, 'end'),
            ('end', False, 'end'),
            ('end', True, 'end'),
        ]
        for from_env, pass_or_fail, to_env in transitions:
            self.add_transition(from_env, pass_or_fail, to_env)

    def set_transition_funcs(self) -> None:
        transition_funcs: Dict[Tuple[str, str], Callable[..., Any]] = {
            ('start', 'start'): self.from_start_to_start,
            ('start', 'paper_submission'): self.from_start_to_paper_submission,
            (
                'paper_submission',
                'peer_review',
            ): self.from_paper_submission_to_peer_review,
            (
                'paper_submission',
                'paper_submission',
            ): self.from_paper_submission_to_paper_submission,
            ('peer_review', 'peer_review'): self.from_peer_review_to_peer_review,
            ('peer_review', 'end'): self.from_peer_review_to_end,
            ('end', 'end'): self.from_end_to_end,
        }
        for (from_env, to_env), func in transition_funcs.items():
            self.add_transition_func(from_env, func, to_env)

    def from_start_to_start(self, env: StartEnv) -> Dict[str, Any]:
        return {}

    def from_start_to_paper_submission(
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

    def from_paper_submission_to_peer_review(
        self,
        env: PaperSubmissionEnv,
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

    def from_paper_submission_to_paper_submission(
        self, env: PaperSubmissionEnv
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

    def from_peer_review_to_end(self, env: PeerReviewEnv) -> Dict[str, Any]:
        return {'meta_review': env.meta_review}

    def from_peer_review_to_peer_review(self, env: PeerReviewEnv) -> Dict[str, Any]:
        proj_leader = env.proj_leader.profile
        reviewers = self.find_reviewers(env.paper, 2)
        chair = self.find_chair(env.paper)
        return {
            'agent_profiles': [proj_leader] + reviewers + [chair],
            'agent_roles': ['proj_leader'] + ['reviewer'] * 2 + ['chair'],
            'agent_models': ['gpt-4o'] * 4,
            'paper': env.paper,
        }

    def from_end_to_end(self, env: EndEnv) -> Dict[str, Any]:
        return {}
