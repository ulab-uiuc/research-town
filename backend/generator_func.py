import os
from typing import Generator, Optional, Tuple

from research_town.agents import Agent
from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, Progress, ProgressDB
from research_town.engines import Engine
from research_town.utils.paper_collector import get_intro
from research_town.agents import Agent


def run_engine(
    url: str,
) -> Generator[Tuple[Optional[Progress], Optional[Agent]], None, None]:
    # Get the introduction of the paper from the URL
    intro = get_intro(url)

    # If no introduction found, return None
    if not intro:
        yield None, None
        return

    # Paths for configurations and logs
    config_file_path = '../configs'
    save_file_path = '../examples/research_town_demo_log'

    # List of agent names (researchers)
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

    # Load or initialize the research databases
    config = Config(config_file_path)
    profile_db = ProfileDB()
    paper_db = PaperDB()

    # Load existing data if available, otherwise pull new data
    if os.path.exists(save_file_path):
        profile_db.load_from_json(save_file_path, with_embed=True)
        paper_db.load_from_json(save_file_path, with_embed=True)
    else:
        profile_db.pull_profiles(agent_names=agent_names, config=config)
        paper_db.pull_papers(num=10, domain='graph neural networks')

    # Initialize databases for logging and tracking progress
    log_db = LogDB()
    progress_db = ProgressDB()

    # Set up the research engine with the loaded databases
    engine = Engine(
        project_name='research_town_demo',
        profile_db=profile_db,
        paper_db=paper_db,
        progress_db=progress_db,
        log_db=log_db,
        config=config,
    )

    # Start the engine with the paper introduction
    engine.start(contexts=[intro])

    # Run the engine through different states until it reaches the end
    while engine.curr_env.name != 'end':
        run_result = engine.curr_env.run()

        if run_result:
            for progress, agent in run_result:
                yield progress, agent
                engine.time_step += 1

        engine.transition()
