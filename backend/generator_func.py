import os
from typing import Generator, Optional, Tuple

from research_town.agents import Agent
from research_town.configs import Config
from research_town.data import Progress, Prompt
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB
from research_town.engines import Engine
from research_town.utils.paper_collector import get_paper_introduction


def run_engine(
    url: str,
) -> Generator[
    Tuple[Optional[Progress], Optional[Agent], Optional[Prompt]], None, None
]:
    try:
        intro = get_paper_introduction(url)
        if not intro:
            yield None, None, None
            return

        config_file_path = '../configs'
        profile_file_path = '../examples/profiles'
        paper_file_path = '../examples/papers'

        config = Config(config_file_path)
        profile_db = ProfileDB()
        paper_db = PaperDB()

        if os.path.exists(paper_file_path) and os.path.exists(profile_file_path):
            profile_db.load_from_json(profile_file_path, with_embed=True)
            paper_db.load_from_json(paper_file_path, with_embed=True)
        else:
            raise FileNotFoundError('Profile and paper databases not found.')

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

            if run_result:
                for progress, agent, prompt in run_result:
                    yield progress, agent, prompt
                    engine.time_step += 1

            engine.transition()
    except Exception as e:
        print(f'Error occurred during engine execution: {e}')

    finally:
        print('Engine execution completed.')
