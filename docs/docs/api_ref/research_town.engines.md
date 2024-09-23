# research_town.engines package

## Submodules

## research_town.engines.engine module

### *class* research_town.engines.engine.Engine(project_name: str, profile_db: [ProfileDB](research_town.dbs.md#research_town.dbs.db_profile.ProfileDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), time_step: int = 0)

Bases: [`BaseEngine`](#research_town.engines.engine_base.BaseEngine)

#### set_envs() → None

#### set_transitions() → None

## research_town.engines.engine_base module

### *class* research_town.engines.engine_base.BaseEngine(project_name: str, profile_db: [ProfileDB](research_town.dbs.md#research_town.dbs.db_profile.ProfileDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), time_step: int = 0)

Bases: `object`

#### add_envs(envs: List[[BaseEnv](research_town.envs.md#research_town.envs.env_base.BaseEnv)]) → None

#### add_transitions(transitions: List[Tuple[str, str, str]]) → None

#### record(progress: [Progress](research_town.dbs.md#research_town.dbs.data.Progress), agent: [Agent](research_town.agents.md#research_town.agents.agent.Agent)) → None

#### run(contexts: List[str]) → None

#### save(save_file_path: str, with_embed: bool = False) → None

#### set_envs() → None

#### set_transitions() → None

#### start(contexts: List[str]) → None

#### transition() → None

## Module contents

### *class* research_town.engines.BaseEngine(project_name: str, profile_db: [ProfileDB](research_town.dbs.md#research_town.dbs.db_profile.ProfileDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), time_step: int = 0)

Bases: `object`

#### add_envs(envs: List[[BaseEnv](research_town.envs.md#research_town.envs.env_base.BaseEnv)]) → None

#### add_transitions(transitions: List[Tuple[str, str, str]]) → None

#### record(progress: [Progress](research_town.dbs.md#research_town.dbs.data.Progress), agent: [Agent](research_town.agents.md#research_town.agents.agent.Agent)) → None

#### run(contexts: List[str]) → None

#### save(save_file_path: str, with_embed: bool = False) → None

#### set_envs() → None

#### set_transitions() → None

#### start(contexts: List[str]) → None

#### transition() → None

### *class* research_town.engines.Engine(project_name: str, profile_db: [ProfileDB](research_town.dbs.md#research_town.dbs.db_profile.ProfileDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), time_step: int = 0)

Bases: [`BaseEngine`](#research_town.engines.engine_base.BaseEngine)

#### set_envs() → None

#### set_transitions() → None
