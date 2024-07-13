from beartype.typing import Any, Dict

from ..configs import Config
from ..dbs import AgentProfile, AgentProfileDB, EnvLogDB, PaperProfileDB, ProgressDB
from ..envs import (
    EndMultiAgentEnv,
    PaperSubmissionMultiAgentEnv,
    PeerReviewMultiAgentEnv,
    StartMultiAgentEnv,
)
from .engine_base import BaseResearchEngine


class TwoStageResearchEngine(BaseResearchEngine):
    def __init__(
        self,
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        progress_db: ProgressDB,
        env_db: EnvLogDB,
        config: Config,
        time_step: int = 0,
        stop_flag: bool = False,
    ) -> None:
        super().__init__(
            agent_db=agent_db,
            paper_db=paper_db,
            progress_db=progress_db,
            env_db=env_db,
            config=config,
            time_step=time_step,
            stop_flag=stop_flag,
        )
        self.set_dbs()
        self.set_envs()
        self.set_transitions()
        self.set_transition_funcs()

    def set_envs(self) -> None:
        self.add_env(
            'start',
            StartMultiAgentEnv(
                env_db=self.env_db,
                progress_db=self.progress_db,
                paper_db=self.paper_db,
                config=self.config,
            ),
        )
        self.add_env(
            'paper_submission',
            PaperSubmissionMultiAgentEnv(
                env_db=self.env_db,
                progress_db=self.progress_db,
                paper_db=self.paper_db,
                config=self.config,
            ),
        )
        self.add_env(
            'peer_review',
            PeerReviewMultiAgentEnv(
                env_db=self.env_db,
                progress_db=self.progress_db,
                paper_db=self.paper_db,
                config=self.config,
            ),
        )
        self.add_env(
            'end',
            EndMultiAgentEnv(
                env_db=self.env_db,
                progress_db=self.progress_db,
                paper_db=self.paper_db,
                config=self.config,
            ),
        )

    def enter_env(self, env_name: str, proj_leader: AgentProfile) -> None:
        if env_name not in self.envs:
            raise ValueError(f'env {env_name} not found')

        self.curr_env_name = env_name
        self.curr_env = self.envs[env_name]
        self.curr_env.on_enter(
            time_step=self.time_step,
            stop_flag=self.stop_flag,
            agent_profiles=[proj_leader],
            agent_roles=['proj_leader'],
            agent_models=['gpt-4o'],
        )

    def set_transitions(self) -> None:
        self.add_transition('start', True, 'paper_submission')
        self.add_transition('start', False, 'paper_submission')
        self.add_transition('paper_submission', True, 'peer_review')
        self.add_transition('paper_submission', False, 'paper_submission')
        self.add_transition('peer_review', False, 'peer_review')
        self.add_transition('peer_review', True, 'end')
        self.add_transition('end', False, 'end')
        self.add_transition('end', True, 'end')

    def set_transition_funcs(self) -> None:
        self.add_transition_func('start', self.from_start_to_start, 'start')
        self.add_transition_func(
            'start', self.from_start_to_paper_submission, 'paper_submission'
        )
        self.add_transition_func(
            'paper_submission', self.from_paper_submission_to_peer_review, 'peer_review'
        )
        self.add_transition_func(
            'paper_submission',
            self.from_paper_submission_to_paper_submission,
            'paper_submission',
        )
        self.add_transition_func(
            'peer_review', self.from_peer_review_to_peer_review, 'peer_review'
        )
        self.add_transition_func('peer_review', self.from_peer_review_to_end, 'end')
        self.add_transition_func('end', self.from_end_to_end, 'end')

    def from_start_to_start(self, env: StartMultiAgentEnv) -> Dict[str, Any]:
        return {}

    def from_start_to_paper_submission(
        self,
        env: StartMultiAgentEnv,
        proj_participant_num: int = 1,
    ) -> Dict[str, Any]:
        proj_leader = env.proj_leader.profile
        proj_participants = self.find_proj_participants(
            proj_leader,
            proj_participant_num=proj_participant_num,
        )

        return {
            'agent_profiles': [proj_leader] + proj_participants,
            'agent_roles': ['proj_leader']
            + ['proj_participant'] * proj_participant_num,
            'agent_models': ['gpt-4o'] * (proj_participant_num + 1),
        }

    def from_paper_submission_to_peer_review(
        self,
        env: PaperSubmissionMultiAgentEnv,
        reviewer_num: int = 1,
    ) -> Dict[str, Any]:
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
        self,
        env: PaperSubmissionMultiAgentEnv,
        proj_participant_num: int = 2,
    ) -> Dict[str, Any]:
        proj_leader = env.proj_leader.profile
        proj_participants = self.find_proj_participants(
            proj_leader,
            proj_participant_num=proj_participant_num,
        )

        return {
            'agent_profiles': [proj_leader] + proj_participants,
            'agent_roles': ['proj_leader']
            + ['proj_participant'] * proj_participant_num,
            'agent_models': ['gpt-4o'] * (proj_participant_num + 1),
        }

    def from_peer_review_to_end(self, env: PeerReviewMultiAgentEnv) -> Dict[str, Any]:
        return {'meta_review': env.meta_review}

    def from_peer_review_to_peer_review(
        self, env: PeerReviewMultiAgentEnv
    ) -> Dict[str, Any]:
        proj_leader = env.proj_leader.profile
        reviewers = self.find_reviewers(env.paper, 2)
        chair = self.find_chair(env.paper)
        return {
            'agent_profiles': [proj_leader] + reviewers + [chair],
            'agent_roles': ['proj_leader'] + ['reviewer'] * 2 + ['chair'],
            'agent_models': ['gpt-4o'] * 4,
            'paper': env.paper,
        }

    def from_end_to_end(self, env: EndMultiAgentEnv) -> Dict[str, Any]:
        return {}
