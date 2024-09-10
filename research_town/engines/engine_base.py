import os
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple

from ..configs import Config
from ..dbs import LogDB, PaperDB, ProgressDB, Proposal, Researcher, ResearcherDB
from ..envs.env_base import BaseEnv
from ..dbs import Idea, Review, Rebuttal, MetaReview, Insight
from ..dbs import IdeaBrainstormingLog, LiteratureReviewLog, ProposalWritingLog, ReviewWritingLog, RebuttalWritingLog, MetaReviewWritingLog


class BaseEngine:
    def __init__(
        self,
        project_name: str,
        agent_db: ResearcherDB,
        paper_db: PaperDB,
        progress_db: ProgressDB,
        env_db: LogDB,
        config: Config,
        time_step: int = 0,
        stop_flag: bool = False,
    ) -> None:
        self.project_name = project_name
        self.agent_db = agent_db
        self.paper_db = paper_db
        self.progress_db = progress_db
        self.env_db = env_db
        self.config = config
        self.time_step = time_step
        self.stop_flag = stop_flag
        self.model_name = self.config.param.base_llm
        self.envs: Dict[str, BaseEnv] = {}
        self.transition_funcs: Dict[Tuple[str, str], Callable[..., Any]] = {}
        self.transitions: Dict[str, Dict[bool, str]] = defaultdict(dict)
        self.set_dbs()
        self.set_envs()
        self.set_transitions()
        self.set_transition_funcs()

    def set_dbs(self) -> None:
        self.agent_db.reset_role_avaialbility()
        self.env_db.set_project_name(self.project_name)
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
            self.add_transition_func(from_env, func, to_env)

    def add_transitions(self, transitions: List[Tuple[str, bool, str]]) -> None:
        for from_env, pass_or_fail, to_env in transitions:
            self.transitions[from_env][pass_or_fail] = to_env

    def start(self, task: str, env_name: str = 'start') -> None:
        if env_name not in self.envs:
            raise ValueError(f'env {env_name} not found')

        self.curr_env_name = env_name
        self.curr_env = self.envs[env_name]
        leader = self.find_agents(
            condition={}, query=task, num=1, update_fields={}
        )[0]
        self.curr_env.on_enter(
            time_step=self.time_step,
            stop_flag=self.stop_flag,
            agent_profiles=[leader],
            agent_roles=['leader'],
            agent_models=[self.model_name],
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

    def run(self, task: str) -> None:
        self.start(task=task)
        while self.curr_env_name != 'end':
            progress, agent = self.curr_env.run()
            self.sync_dbs(progress, agent)
            self.time_step += 1
            self.transition()

    def save(self, save_file_path: str, with_embed: bool = False) -> None:
        if not os.path.exists(save_file_path):
            os.makedirs(save_file_path)

        self.agent_db.save_to_json(save_file_path, with_embed=with_embed)
        self.paper_db.save_to_json(save_file_path, with_embed=with_embed)
        self.progress_db.save_to_json(save_file_path)
        self.env_db.save_to_json(save_file_path)

    def load(self) -> None:
        pass

    def sync_dbs(self, progress: Any, agent: Researcher) -> None:
        self.progress_db.add(progress)
        if isinstance(progress, Insight):
            self.env_db.add(
                LiteratureReviewLog(
                    time_step=self.time_step,
                    agent_pk=agent.profile.pk,
                    paper_pk=progress.paper_pk,
                    insight_pk=progress.pk,
                )
            )

        if isinstance(progress, Idea):
            self.env_db.add(
                IdeaBrainstormingLog(
                    time_step=self.time_step,
                    agent_pk=agent.profile.pk,
                    idea_pk=progress.pk,
                )
            )

        if isinstance(progress, Proposal):
            self.env_db.add(
                ProposalWritingLog(
                    time_step=self.time_step,
                    agent_pk=agent.profile.pk,
                    proposal_pk=progress.pk,
                )
            )

        if isinstance(progress, Review):
            self.env_db.add(
                ReviewWritingLog(
                    time_step=self.time_step,
                    agent_pk=agent.profile.pk,
                    paper_pk=progress.paper_pk,
                    review_pk=progress.pk,
                )
            )
        if isinstance(progress, Rebuttal):
            self.env_db.add(
                RebuttalWritingLog(
                    time_step=self.time_step,
                    agent_pk=agent.profile.pk,
                    paper_pk=progress.paper_pk,
                    rebuttal_pk=progress.pk,
                )
            )
        if isinstance(progress, MetaReview):
            self.env_db.add(
                MetaReviewWritingLog(
                    time_step=self.time_step,
                    agent_pk=agent.profile.pk,
                    paper_pk=progress.paper_pk,
                    meta_review_pk=progress.pk,
                )
            )
