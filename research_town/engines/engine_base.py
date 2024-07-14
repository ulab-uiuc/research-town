import os
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple

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
        self.transition_funcs: Dict[Tuple[str, str], Callable[..., Any]] = {}
        self.transitions: Dict[str, Dict[bool, str]] = defaultdict(dict)
        self.set_dbs()
        self.set_envs()
        self.set_transitions()
        self.set_transition_funcs()

    def set_dbs(self) -> None:
        self.agent_db.reset_role_avaialbility()

    def set_envs(self) -> None:
        pass

    def set_transitions(self) -> None:
        pass

    def set_transition_funcs(self) -> None:
        pass

    def add_env(self, name: str, env: BaseMultiAgentEnv) -> None:
        self.envs[name] = env

    def add_transition_func(
        self, from_env: str, func: Callable[..., Any], to_env: str
    ) -> None:
        self.transition_funcs[(from_env, to_env)] = func

    def add_transition(self, from_env: str, pass_or_fail: bool, to_env: str) -> None:
        self.transitions[from_env][pass_or_fail] = to_env

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
        self.curr_env = self.envs[self.curr_env_name]
        self.curr_env.on_enter(
            time_step=self.time_step,
            stop_flag=self.stop_flag,
            **input_data,
        )

    def find_agents(
        self,
        condition: Dict[str, Any],
        query: str,
        num: int,
        update_fields: Dict[str, bool],
    ) -> List[AgentProfile]:
        candidates = self.agent_db.get(**condition)
        selected_agents = self.agent_db.match(
            query=query, agent_profiles=candidates, num=num
        )

        for agent in selected_agents:
            for field, value in update_fields.items():
                setattr(agent, field, value)
            self.agent_db.update(pk=agent.pk, updates=agent.model_dump())

        return selected_agents

    def set_proj_leader(self, proj_leader: AgentProfile) -> AgentProfile:
        return self.find_agents(
            condition={'pk': proj_leader.pk},
            query=proj_leader.bio,
            num=1,
            update_fields={
                'is_proj_leader_candidate': True,
                'is_proj_participant_candidate': False,
                'is_reviewer_candidate': False,
                'is_chair_candidate': False,
            },
        )[0]

    def find_proj_participants(
        self, proj_leader: AgentProfile, proj_participant_num: int
    ) -> List[AgentProfile]:
        return self.find_agents(
            condition={'is_proj_participant_candidate': True},
            query=proj_leader.bio,
            num=proj_participant_num,
            update_fields={
                'is_proj_leader_candidate': False,
                'is_proj_participant_candidate': True,
                'is_reviewer_candidate': False,
                'is_chair_candidate': False,
            },
        )

    def find_reviewers(
        self, paper_submission: ResearchPaperSubmission, reviewer_num: int
    ) -> List[AgentProfile]:
        return self.find_agents(
            condition={'is_reviewer_candidate': True},
            query=paper_submission.abstract,
            num=reviewer_num,
            update_fields={
                'is_proj_leader_candidate': False,
                'is_proj_participant_candidate': False,
                'is_reviewer_candidate': True,
                'is_chair_candidate': False,
            },
        )

    def find_chair(self, paper_submission: ResearchPaperSubmission) -> AgentProfile:
        return self.find_agents(
            condition={'is_chair_candidate': True},
            query=paper_submission.abstract,
            num=1,
            update_fields={
                'is_proj_leader_candidate': False,
                'is_proj_participant_candidate': False,
                'is_reviewer_candidate': False,
                'is_chair_candidate': True,
            },
        )[0]

    def recover(self) -> None:
        pass

    def run(self) -> None:
        while self.curr_env_name != 'end':
            self.curr_env.run()
            self.time_step += 1
            self.transition()

    def save(self, save_file_path: str) -> None:
        if not os.path.exists(os.path.dirname(save_file_path)):
            os.makedirs(os.path.dirname(save_file_path))

        self.agent_db.save_to_json(save_file_path)
        self.paper_db.save_to_json(save_file_path)
        self.progress_db.save_to_json(save_file_path)
        self.env_db.save_to_json(save_file_path)
