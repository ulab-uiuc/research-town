import json
import os
from typing import Generator

from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB, Progress
from research_town.engines import Engine
from research_town.utils.paper_collector import get_intro
from research_town.utils.serializer import Serializer


def run_engine(url: str) -> Generator[Progress, None, None]:
    intro = get_intro(url)
    if intro is None:
        yield 'Error: invalid URL\n'
        return
    config_file_path = '../configs'
    save_file_path = '../examples/research_town_demo_log'
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
    serializer = Serializer()
    # Load or initialize databases
    config = Config(config_file_path)
    profile_db = ProfileDB()
    paper_db = PaperDB()
    if os.path.exists(save_file_path):
        profile_db.load_from_json(save_file_path, with_embed=True)
        paper_db.load_from_json(save_file_path, with_embed=True)
    else:
        profile_db.pull_profiles(agent_names=agent_names, config=config)
        paper_db.pull_papers(num=10, domain='graph neural networks')

    log_db = LogDB()
    progress_db = ProgressDB()
    engine = Engine(
        project_name='research_town_demo',
        profile_db=profile_db,
        paper_db=paper_db,
        progress_db=progress_db,
        log_db=log_db,
        config=config,
    )
    engine.start(contexts=[intro])
    while engine.curr_env.name != 'end':
        run_result = engine.curr_env.run()
        if run_result is not None:
            for progress, _ in run_result:
                yield progress
                engine.time_step += 1
        engine.transition()
