from ..configs import Config
from ..dbs import AgentProfileDB, EnvLogDB, PaperProfileDB, ProgressDB
from .engine_base import BaseResearchEngine


class SimpleResearchEngine(BaseResearchEngine):
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
