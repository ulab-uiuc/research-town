# research_town.envs package

## Submodules

## research_town.envs.env_base module

### *class* research_town.envs.env_base.BaseEnv(name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config))

Bases: `ABC`

#### *abstract* on_enter(\*\*context: Any) → None

#### *abstract* on_exit() → Tuple[str, Dict[str, Any]]

#### *abstract* run() → Generator[Tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

## research_town.envs.env_end module

### *class* research_town.envs.env_end.EndEnv(name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

## research_town.envs.env_proposal_writing module

### *class* research_town.envs.env_proposal_writing.ProposalWritingEnv(name: str, log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

## research_town.envs.env_review_writing module

### *class* research_town.envs.env_review_writing.ReviewWritingEnv(name: str, log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

## research_town.envs.env_start module

### *class* research_town.envs.env_start.StartEnv(name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

## Module contents

### *class* research_town.envs.BaseEnv(name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config))

Bases: `ABC`

#### *abstract* on_enter(\*\*context: Any) → None

#### *abstract* on_exit() → Tuple[str, Dict[str, Any]]

#### *abstract* run() → Generator[Tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

### *class* research_town.envs.EndEnv(name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

### *class* research_town.envs.ProposalWritingEnv(name: str, log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

### *class* research_town.envs.ReviewWritingEnv(name: str, log_db: [LogDB](research_town.dbs.md#research_town.dbs.db_log.LogDB), progress_db: [ProgressDB](research_town.dbs.md#research_town.dbs.db_progress.ProgressDB), paper_db: [PaperDB](research_town.dbs.md#research_town.dbs.db_paper.PaperDB), config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]

### *class* research_town.envs.StartEnv(name: str, config: [Config](research_town.configs.md#research_town.configs.config.Config), agent_manager: [AgentManager](research_town.agents.md#research_town.agents.agent_manager.AgentManager))

Bases: [`BaseEnv`](#research_town.envs.env_base.BaseEnv)

#### on_enter(\*\*context: Any) → None

#### on_exit() → tuple[str, dict[str, Any]]

#### run() → Generator[tuple[[Progress](research_town.dbs.md#research_town.data.Progress), [Agent](research_town.agents.md#research_town.agents.agent.Agent)], None, None]
