import os
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple
from ..configs import Config
from ..dbs import AgentProfile, AgentProfileDB, EnvLogDB, PaperProfileDB, ProgressDB, ResearchProposal
from ..envs.env_base import BaseMultiAgentEnv

class BaseEngine:
    def __init__(self, project_name: str, agent_db: AgentProfileDB, paper_db: PaperProfileDB, 
                 progress_db: ProgressDB, env_db: EnvLogDB, config: Config, time_step: int = 0, stop_flag: bool = False) -> None:
        self.project_name, self.config = project_name, config
        self.agent_db, self.paper_db, self.progress_db, self.env_db = agent_db, paper_db, progress_db, env_db
        self.time_step, self.stop_flag = time_step, stop_flag
        self.envs, self.transition_funcs, self.transitions = {}, {}, defaultdict(dict)
        self._initialize()

    def _initialize(self) -> None:
        self.agent_db.reset_role_avaialbility()
        self.env_db.set_project_name(self.project_name)
        self.progress_db.set_project_name(self.project_name)
        self.set_envs()
        self.set_transitions()
        self.set_transition_funcs()

    def add_env(self, name: str, env: BaseMultiAgentEnv) -> None:
        self.envs[name] = env

    def add_transition_func(self, from_env: str, func: Callable[..., Any], to_env: str) -> None:
        self.transition_funcs[(from_env, to_env)] = func

    def add_transition(self, from_env: str, pass_or_fail: bool, to_env: str) -> None:
        self.transitions[from_env][pass_or_fail] = to_env

    def start(self, task: str, env_name: str = 'start') -> None:
        if env_name not in self.envs:
            raise ValueError(f'env {env_name} not found')
        self.curr_env_name, self.curr_env = env_name, self.envs[env_name]
        proj_leader = self.find_agents({}, task, 1, {})[0]
        self.curr_env.on_enter(self.time_step, self.stop_flag, [proj_leader], ['proj_leader'], ['gpt-4o'])

    def transition(self) -> None:
        pass_or_fail = self.curr_env.on_exit()
        next_env_name = self.transitions[self.curr_env_name][pass_or_fail]
        input_data = self.transition_funcs.get((self.curr_env_name, next_env_name), lambda x: {})(self.curr_env)
        self.curr_env_name, self.curr_env = next_env_name, self.envs[next_env_name]
        self.curr_env.on_enter(self.time_step, self.stop_flag, **input_data)

    def find_agents(self, condition: Dict[str, Any], query: str, num: int, update_fields: Dict[str, bool]) -> List[AgentProfile]:
        candidates = self.agent_db.get(**condition)
        selected_agents = self.agent_db.match(query=query, agent_profiles=candidates, num=num)
        for agent in selected_agents:
            for field, value in update_fields.items():
                setattr(agent, field, value)
            self.agent_db.update(pk=agent.pk, updates=agent.model_dump())
        return selected_agents

    def run(self, task: str) -> None:
        self.start(task)
        while self.curr_env_name != 'end':
            self.curr_env.run()
            self.time_step += 1
            self.transition()

    def save(self, save_file_path: str, with_embed: bool = False) -> None:
        os.makedirs(save_file_path, exist_ok=True)
        for db in [self.agent_db, self.paper_db, self.progress_db, self.env_db]:
            db.save_to_json(save_file_path, with_embed=with_embed)

    def set_envs(self) -> None: pass
    def set_transitions(self) -> None: pass
    def set_transition_funcs(self) -> None: pass
