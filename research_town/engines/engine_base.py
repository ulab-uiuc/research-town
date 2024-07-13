from typing import Dict

from beartype.typing import List

from ..configs import Config
from ..dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfileDB,
    ProgressDB,
    ResearchPaperSubmission,
)
from ..envs.env_base import BaseMultiAgentEnv


class BaseResearchEngine:
    def __init__(
        self,
        agent_db: AgentProfileDB,
        paper_db: PaperProfileDB,
        progress_db: ProgressDB,
        env_db: EnvLogDB,
        config: Config,
    ) -> None:
        self.time_step = 0
        self.envs: Dict[str, BaseMultiAgentEnv] = {}
        self.transition_matrix: Dict[str, Dict[bool, str]] = {}
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.progress_db = progress_db
        self.env_db = env_db
        self.config = config

    def add_env(self, name: str, env: BaseMultiAgentEnv) -> None:
        self.envs[name] = env

    def set_transition(self, from_name: str, pass_name: str, fail_name: str) -> None:
        self.transition_matrix[from_name] = {True: pass_name, False: fail_name}

    def set_init_env(self, name: str) -> None:
        # start a new round of the research project
        self.agent_db.reset_role_avaialbility()
        if name not in self.envs:
            raise ValueError(f'Env {name} not found')

        self.curr_env_name = name
        self.curr_env = self.envs[name]
        self.curr_env.on_enter()

    def update(self) -> None:
        if self.curr_env_name:
            self.curr_env.update()
            self.time_step += 1

    def transition(self) -> None:
        if self.curr_env:
            result = self.curr_env.on_exit()
            next_env_name = self.transition_matrix[self.curr_env_name][result]
            self.curr_env_name = next_env_name
            self.curr_env = self.envs[next_env_name]
            self.curr_env.on_enter()

    def set_proj_leader(
        self,
        proj_leader: AgentProfile,
    ) -> None:
        proj_leader.is_proj_leader_candidate = True
        proj_leader.is_proj_participant_candidate = False
        proj_leader.is_reviewer_candidate = False
        proj_leader.is_chair_candidate = False
        self.agent_db.update(pk=proj_leader.pk, updates=proj_leader.model_dump())
        return proj_leader

    def find_proj_participants(
        self,
        proj_leader: AgentProfile,
        proj_participant_num: int,
    ) -> List[AgentProfile]:
        # Find available project participants
        conditions = {'is_proj_participant_candidate': True}
        proj_participant_candidates = self.agent_db.get(**conditions)

        # Find most suitable project participants
        proj_leader_bio = proj_leader.bio
        proj_participants = self.agent_db.match(
            query=[proj_leader_bio],
            agent_profiles=proj_participant_candidates,
            num=proj_participant_num,
        )

        # update the db to does allow participants to be selected as reviewers or chairs
        for proj_participant in proj_participants:
            proj_participant.is_proj_leader_candidate = False
            proj_participant.is_proj_participant_candidate = True
            proj_participant.is_reviewer_candidate = False
            proj_participant.is_chair_candidate = False
            self.agent_db.update(
                pk=proj_participant.pk, updates=proj_participant.model_dump()
            )

        return proj_participants

    def find_reviewers(
        self,
        paper_submission: ResearchPaperSubmission,
        reviewer_num: int,
    ) -> List[AgentProfile]:
        # Find potential reviewers
        conditions = {'is_reviewer_candidate': True}
        reviewer_candidates = self.agent_db.get(**conditions)

        # Find most suitable reviewers
        paper_abstract = paper_submission.abstract
        reviewers = self.agent_db.match(
            query=[paper_abstract], agent_profiles=reviewer_candidates, num=reviewer_num
        )

        # update the db to does allow reviewers to be selected as chairs
        for reviewer in reviewers:
            reviewer.is_proj_leader_candidate = False
            reviewer.is_proj_participant_candidate = False
            reviewer.is_reviewer_candidate = True
            reviewer.is_chair_candidate = False
            self.agent_db.update(pk=reviewer.pk, updates=reviewer.model_dump())

        return reviewers

    def find_chair(
        self,
        paper_submission: ResearchPaperSubmission,
    ) -> AgentProfile:
        # Find potential chairs
        conditions = {'is_chair_candidate': True}
        chair_candidates = self.agent_db.get(**conditions)

        # Find most suitable chairs
        paper_abstract = paper_submission.abstract
        chair = self.agent_db.match(
            query=[paper_abstract], agent_profiles=chair_candidates
        )[0]

        # update the db to does allow chairs to be selected as reviewers
        chair.is_proj_leader_candidate = False
        chair.is_proj_participant_candidate = False
        chair.is_reviewer_candidate = False
        chair.is_chair_candidate = True
        self.agent_db.update(pk=chair.pk, updates=chair.model_dump())

        return chair

    def recover(self) -> None:
        pass
