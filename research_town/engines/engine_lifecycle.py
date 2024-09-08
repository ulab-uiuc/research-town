from ..envs import (
    EndMultiAgentEnv,
    PaperSubmissionMultiAgentEnv,
    PeerReviewMultiAgentEnv,
    StartMultiAgentEnv,
)
from .engine_base import BaseEngine


class LifecycleEngine(BaseEngine):
    def set_envs(self) -> None:
        envs = {
            'start': StartMultiAgentEnv,
            'paper_submission': PaperSubmissionMultiAgentEnv,
            'peer_review': PeerReviewMultiAgentEnv,
            'end': EndMultiAgentEnv,
        }
        for name, env_class in envs.items():
            self.add_env(
                name,
                env_class(self.env_db, self.progress_db, self.paper_db, self.config),
            )

    def set_transitions(self) -> None:
        for transition in [
            ('start', True, 'paper_submission'),
            ('start', False, 'paper_submission'),
            ('paper_submission', True, 'peer_review'),
            ('paper_submission', False, 'paper_submission'),
            ('peer_review', True, 'end'),
            ('peer_review', False, 'peer_review'),
            ('end', True, 'end'),
            ('end', False, 'end'),
        ]:
            self.add_transition(*transition)

    def set_transition_funcs(self) -> None:
        funcs = {
            ('start', 'paper_submission'): self._start_to_paper_submission,
            ('paper_submission', 'peer_review'): self._paper_to_peer_review,
            ('peer_review', 'end'): self._peer_review_to_end,
        }
        for key, func in funcs.items():
            self.add_transition_func(*key, func)

    def _start_to_paper_submission(self, env: StartMultiAgentEnv) -> Dict[str, Any]:
        participants = self.find_proj_participants(
            env.proj_leader.profile, self.config.param.proj_participant_num
        )
        return {
            'agent_profiles': [env.proj_leader.profile] + participants,
            'agent_roles': ['proj_leader'] + ['proj_participant'] * len(participants),
            'agent_models': ['gpt-4o'] * (len(participants) + 1),
        }

    def _paper_to_peer_review(
        self, env: PaperSubmissionMultiAgentEnv
    ) -> Dict[str, Any]:
        reviewers = self.find_reviewers(env.paper, self.config.param.reviewer_num)
        return {
            'agent_profiles': [env.proj_leader.profile]
            + reviewers
            + [self.find_chair(env.paper)],
            'agent_roles': ['proj_leader'] + ['reviewer'] * len(reviewers) + ['chair'],
            'agent_models': ['gpt-4o'] * (len(reviewers) + 2),
        }

    def _peer_review_to_end(self, env: PeerReviewMultiAgentEnv) -> Dict[str, Any]:
        return {'meta_review': env.meta_review}
