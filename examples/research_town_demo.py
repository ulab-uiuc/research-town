import os

from beartype.typing import Literal

from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProgressDB, AgentDB
from research_town.engines import Engine

Role = Literal['reviewer', 'leader', 'member', 'chair'] | None


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
    # if save path exists, then load
    config = Config(config_file_path)
    agent_db = AgentDB()
    paper_db = PaperDB()
    if os.path.exists(save_file_path):
        agent_db.load_from_json(save_file_path, with_embed=True)
        paper_db.load_from_json(save_file_path, with_embed=True)
    else:
        agent_db.pull_agents(agent_names=agent_names, config=config)
        paper_db.pull_papers(num=10, domain='graph neural networks')

    env_db = LogDB()
    progress_db = ProgressDB()
    engine = Engine(
        project_name='research_town_demo',
        agent_db=agent_db,
        paper_db=paper_db,
        progress_db=progress_db,
        env_db=env_db,
        config=config,
    )
    engine.run(task='Conduct research on Graph Neural Networks (GNN).')
    engine.save(save_file_path=save_file_path, with_embed=True)
    return


def main() -> None:
    run_sync_experiment(
        config_file_path='../configs',
        save_file_path='./research_town_demo_log',
    )


if __name__ == '__main__':
    main()
