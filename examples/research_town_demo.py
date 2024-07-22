from beartype.typing import Literal

from research_town.configs import Config
from research_town.dbs import AgentProfileDB, EnvLogDB, PaperProfileDB, ProgressDB
from research_town.engines import LifecycleResearchEngine

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


def run_sync_experiment(
    config_file_path: str,
    save_file_path: str,
) -> None:
    agent_names = [
        'Jiaxuan You',
        'Jure Leskovec',
        'Stefanie Jegelka',
        'Silvio Lattanzi',
        'Rex Ying',
        'Tim Althoff',
        'Christos Faloutsos',
        'Julian McAuley',
    ]
    config = Config(config_file_path)
    agent_db = AgentProfileDB()
    agent_db.pull_agents(agent_names=agent_names, config=config)
    paper_db = PaperProfileDB()
    paper_db.pull_papers(num=10, domain='graph neural networks')
    env_db = EnvLogDB()
    progress_db = ProgressDB()
    engine = LifecycleResearchEngine(
        project_name='research_town_demo',
        agent_db=agent_db,
        paper_db=paper_db,
        progress_db=progress_db,
        env_db=env_db,
        config=config,
    )
    agent_profile = agent_db.get(name='Jiaxuan You')[0]
    engine.enter_env(env_name='start', proj_leader=agent_profile)
    engine.run()
    engine.save(save_file_path=save_file_path)
    return


def main() -> None:
    run_sync_experiment(
        config_file_path='../configs/default_config.yaml',
        save_file_path='./research_town_demo_log',
    )


if __name__ == '__main__':
    main()
