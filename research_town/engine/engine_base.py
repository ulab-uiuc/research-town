from typing import Dict

from ..envs.env_base import BaseMultiAgentEnv


class BaseResearchEngine:
    def __init__(self) -> None:
        self.time_step = 0
        self.envs: Dict[str, BaseMultiAgentEnv] = {}
        self.transition_matrix: Dict[str, Dict[bool, str]] = {}
        self.curr_env_name: str = ''
        self.curr_env: BaseMultiAgentEnv = None

    def add_env(self, name: str, env: BaseMultiAgentEnv):
        self.envs[name] = env

    def set_transition(self, from_name: str, pass_name: str, fail_name: str):
        self.transition_matrix[from_name] = {True: pass_name, False: fail_name}

    def set_initial_env(self, name: str):
        self.curr_env_name = name
        self.curr_env = self.envs[name]
        self.curr_env.on_enter()

    def update(self):
        if self.curr_env_name:
            self.curr_env.update()

    def transition(self):
        if self.curr_env:
            result = self.curr_env.on_exit()
            next_env_name = self.transition_matrix[self.curr_env_name][result]
            self.curr_env_name = next_env_name
            self.curr_env = self.envs[next_env_name]
            self.curr_env.on_enter()

    def find_proj_participants(self) -> None:
        pass

    def find_proj_leaders(self) -> None:
        pass

    def find_reviewers(self) -> None:
        pass

    def find_chairs(self) -> None:
        pass

    def recover(self) -> None:
        pass
