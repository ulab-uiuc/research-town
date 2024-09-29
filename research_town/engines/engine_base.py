import os
from typing import Dict, List, Tuple, Type

from ..agents import Agent, AgentManager
from ..configs import Config
from ..data.data import (
    Idea,
    IdeaBrainstormLog,
    Insight,
    LiteratureReviewLog,
    Log,
    MetaReview,
    MetaReviewWritingLog,
    Progress,
    Proposal,
    ProposalWritingLog,
    Rebuttal,
    RebuttalWritingLog,
    Review,
    ReviewWritingLog,
)
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
    ) -> None:
        self.project_name = project_name
        self.profile_db = profile_db
        self.paper_db = paper_db
        self.progress_db = progress_db
        self.log_db = log_db
        self.config = config
        self.agent_manager = AgentManager(profile_db=profile_db, config=config)
        self.time_step = time_step

        self.envs: Dict[str, BaseEnv] = {}
        self.transitions: Dict[Tuple[BaseEnv, str], BaseEnv] = {}
        self._setup_dbs()
        self.set_envs()
        self.set_transitions()

    def _setup_dbs(self) -> None:
        self.profile_db.reset_role_availability()
        for db in [self.log_db, self.progress_db]:
            db.set_project_name(self.project_name)

    def set_envs(self) -> None:
        pass

    def set_transitions(self) -> None:
        pass

    def add_envs(self, envs: List[BaseEnv]) -> None:
        self.envs.update({env.name: env for env in envs})

    def add_transitions(self, transitions: List[Tuple[str, str, str]]) -> None:
        for src, trigger, dst in transitions:
            self.transitions[self.envs[src], trigger] = self.envs[dst]

    def start(self, contexts: List[str]) -> None:
        self.curr_env = self.envs['start']
        self.curr_env.on_enter(contexts=contexts)

    def transition(self) -> None:
        trigger, exit_data = self.curr_env.on_exit()
        self.curr_env = self.transitions[(self.curr_env, trigger)]
        self.curr_env.on_enter(**exit_data)

    def run(self, contexts: List[str]) -> None:
        self.start(contexts=contexts)
        while self.curr_env.name != 'end':
            run_result = self.curr_env.run()
            if run_result is not None:
                for progress, agent in run_result:
                    self.record(progress, agent)
                    self.time_step += 1
            self.transition()

    def save(self, save_file_path: str, with_embed: bool = False) -> None:
        os.makedirs(save_file_path, exist_ok=True)
        self.profile_db.save_to_json(save_file_path, with_embed=with_embed)
        self.log_db.save_to_json(save_file_path, with_embed=with_embed)
        self.progress_db.save_to_json(save_file_path, with_embed=with_embed)
        self.paper_db.save_to_json(save_file_path, with_embed=with_embed)

    def record(self, progress: Progress, agent: Agent) -> None:
        log_map: Dict[Type[Progress], Type[Log]] = {
            Insight: LiteratureReviewLog,
            Idea: IdeaBrainstormLog,
            Proposal: ProposalWritingLog,
            Review: ReviewWritingLog,
            Rebuttal: RebuttalWritingLog,
            MetaReview: MetaReviewWritingLog,
        }
        log_class = log_map.get(type(progress))
        if not log_class:
            raise ValueError(f'Unrecognized progress type: {type(progress)}')

        log = log_class(
            time_step=self.time_step,
            profile_pk=agent.profile.pk,
            **{f'{progress.__class__.__name__.lower()}_pk': progress.pk},
        )
        self.progress_db.add(progress)
        self.log_db.add(log)
