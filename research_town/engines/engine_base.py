import os
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple

from ..configs import Config
from ..dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from ..envs.env_base import BaseEnv


class BaseEngine:
    def __init__(
        self,
        project_name: str,
        profile_db: ProfileDB,
        paper_db: PaperDB,
        progress_db: ProgressDB,
        log_db: LogDB,
        config: Config,
        time_step: int = 0,
        stop_flag: bool = False,
    ) -> None:
        self.project_name = project_name
        self.profile_db = profile_db
        self.paper_db = paper_db
        self.progress_db = progress_db
        self.log_db = log_db
        self.config = config
        self.time_step = time_step
        self.stop_flag = stop_flag
        self.model_name = self.config.param.base_llm
        self.envs: Dict[str, BaseEnv] = {}
        self.transition_funcs: Dict[Tuple[str, str], Callable[..., Any]] = {}
        self.transitions: Dict[Tuple[str, str], str] = defaultdict(str)
        self.set_dbs()
        self.set_envs()
        self.set_transitions()
        self.set_transition_funcs()

    def set_dbs(self) -> None:
        self.profile_db.reset_role_avaialbility()
        self.log_db.set_project_name(self.project_name)
        self.progress_db.set_project_name(self.project_name)

    def set_envs(self) -> None:
        pass

    def set_transitions(self) -> None:
        pass

    def set_transition_funcs(self) -> None:
        pass

    def add_envs(self, envs: List[BaseEnv]) -> None:
        for env in envs:
            self.envs[env.name] = env

    def add_transition_funcs(
        self, funcs: List[Tuple[str, Callable[..., Any], str]]
    ) -> None:
        for from_env, func, to_env in funcs:
            self.transition_funcs[from_env, to_env] = func

    def add_transitions(self, transitions: List[Tuple[str, str, str]]) -> None:
        for from_env, trigger, to_env in transitions:
            self.transitions[from_env, trigger] = to_env

    def start(self, task: str, env_name: str = 'start') -> None:
        if env_name not in self.envs:
            raise ValueError(f'env {env_name} not found')

        self.curr_env_name = env_name
        self.curr_env = self.envs[env_name]
        self.curr_env.on_enter(
            time_step=self.time_step,
            kwargs={'task': task},
        )

    def transition(self) -> None:
        trigger = self.curr_env.on_exit()
        next_env_name = self.transitions[self.curr_env_name, trigger]
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

    def run(self, task: str) -> None:
        self.start(task=task)
        while self.curr_env_name != 'end':
            self.curr_env.run()
            self.time_step += 1
            self.transition()

    def save(self, save_file_path: str, with_embed: bool = False) -> None:
        if not os.path.exists(save_file_path):
            os.makedirs(save_file_path)

        self.profile_db.save_to_json(save_file_path, with_embed=with_embed)
        self.paper_db.save_to_json(save_file_path, with_embed=with_embed)
        self.progress_db.save_to_json(save_file_path)
        self.log_db.save_to_json(save_file_path)

    def load(self) -> None:
        pass
