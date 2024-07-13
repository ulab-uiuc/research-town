from collections import defaultdict
from typing import Callable, Dict, Tuple

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
        time_step: int = 0,
        stop_flag: bool = False,
    ) -> None:
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.progress_db = progress_db
        self.env_db = env_db
        self.config = config
        self.time_step = time_step
        self.stop_flag = stop_flag
        self.envs: Dict[str, BaseMultiAgentEnv] = {}
        self.transition_funcs: Dict[Tuple[str, str], Callable] = {}
        self.transitions: Dict[str, Dict[bool, str]] = defaultdict(dict)

    def add_env(self, name: str, env: BaseMultiAgentEnv) -> None:
        self.envs[name] = env

    def add_transition_func(self, from_env: str, func: Callable, to_env: str) -> None:
        self.transition_funcs[(from_env, to_env)] = func

    def add_transition(self, from_env: str, pass_or_fail: bool, to_env: str) -> None:
        self.transitions[from_env][pass_or_fail] = to_env

    def set_dbs(self) -> None:
        self.agent_db.reset_role_avaialbility()

    def set_envs(self) -> None:
        pass

    def set_transitions(self) -> None:
        pass

    def run(self) -> None:
        self.curr_env.run()
        self.time_step += 1

    def transition(self) -> None:
        pass_or_fail = self.curr_env.on_exit()
        next_env_name = self.transitions[self.curr_env_name][pass_or_fail]
        if (self.curr_env_name, next_env_name) in self.transition_funcs:
            input_data = self.transition_funcs[(self.curr_env_name, next_env_name)](
                self.curr_env
            )
        else:
            raise ValueError(
                f'no transition function from {self.curr_env_name} to {next_env_name}'
            )

        self.curr_env_name = next_env_name
        self.envs[self.curr_env_name].on_enter(
            time_step=self.time_step,
            stop_flag=self.stop_flag,
            **input_data,
        )

    def set_proj_leader(
        self,
        proj_leader: AgentProfile,
    ) -> AgentProfile:
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
            query=proj_leader_bio,
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
            query=paper_abstract, agent_profiles=reviewer_candidates, num=reviewer_num
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
            query=paper_abstract, agent_profiles=chair_candidates
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
