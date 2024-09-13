import os
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple

from ..configs import Config
from ..dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from ..dbs.data import Idea, Insight, MetaReview, Profile, Proposal, Rebuttal, Review
from ..dbs.logs import (
    IdeaBrainstormLog,
    LiteratureReviewLog,
    MetaReviewWritingLog,
    ProposalWritingLog,
    RebuttalWritingLog,
    ReviewWritingLog,
)
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
        self.time_step = time_step

        self.envs: Dict[str, BaseEnv] = {}
        self.transitions: Dict[Tuple[str, str], str] = defaultdict(str)
        self.set_dbs()
        self.set_envs()
        self.set_transitions()

    def set_dbs(self) -> None:
        self.profile_db.reset_role_avaialbility()
        self.log_db.set_project_name(self.project_name)
        self.progress_db.set_project_name(self.project_name)

    def set_envs(self) -> None:
        pass

    def set_transitions(self) -> None:
        pass

    def add_envs(self, envs: List[BaseEnv]) -> None:
        for env in envs:
            self.envs[env.name] = env

    def add_transitions(self, transitions: List[Tuple[str, str, str]]) -> None:
        for src, trigger, dst in transitions:
            self.transitions[src, trigger] = dst

    def start(self, task: str, env_name: str = 'start') -> None:
        if env_name not in self.envs:
            raise ValueError(f'env {env_name} not found')

        self.curr_env = self.envs[env_name]
        self.curr_env.on_enter(task=task)

    def transition(self) -> None:
        trigger, exit_data = self.curr_env.on_exit()
        next_env_name = self.transitions[self.curr_env.name, trigger]

        self.curr_env = self.envs[next_env_name]
        self.curr_env.on_enter(**exit_data)

    def run(self, task: str) -> None:
        self.start(task=task)
        transition_count = 0
        while self.curr_env.name != 'end':
            if self.curr_env.run():
                for progress, profile in self.curr_env.run():
                    self.record(progress, profile)
                    self.time_step += 1
            self.transition()
            transition_count += 1
            if transition_count > self.config.param.max_transitions:
                break

    def save(self, save_file_path: str, with_embed: bool = False) -> None:
        if not os.path.exists(save_file_path):
            os.makedirs(save_file_path)

        self.profile_db.save_to_json(save_file_path, with_embed=with_embed)
        self.paper_db.save_to_json(save_file_path, with_embed=with_embed)
        self.progress_db.save_to_json(save_file_path)
        self.log_db.save_to_json(save_file_path)

    def record(self, progress: Any, profile: Profile) -> None:
        if isinstance(progress, Insight):
            log = LiteratureReviewLog(
                time_step=self.time_step,
                profile_pk=profile.pk,
                insight_pk=progress.pk,
            )
        elif isinstance(progress, Idea):
            log = IdeaBrainstormLog(
                time_step=self.time_step,
                profile_pk=profile.pk,
                idea_pk=progress.pk,
            )
        elif isinstance(progress, Proposal):
            log = ProposalWritingLog(
                time_step=self.time_step,
                profile_pk=profile.pk,
                proposal_pk=progress.pk,
            )
        elif isinstance(progress, Review):
            log = ReviewWritingLog(
                time_step=self.time_step,
                profile_pk=profile.pk,
                review_pk=progress.pk,
            )
        elif isinstance(progress, Rebuttal):
            log = RebuttalWritingLog(
                time_step=self.time_step,
                profile_pk=profile.pk,
                rebuttal_pk=progress.pk,
            )
        elif isinstance(progress, MetaReview):
            log = MetaReviewWritingLog(
                time_step=self.time_step,
                profile_pk=profile.pk,
                meta_review_pk=progress.pk,
            )
        else:
            raise ValueError(f'progress {progress} not recognized')

        self.progress_db.add(progress)
        self.log_db.add(log)
