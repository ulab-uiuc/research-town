from typing import Generator, Optional, Tuple

from research_town.agents import Agent
from research_town.data import Progress
from research_town.engines import Engine
from research_town.utils.paper_collector import get_paper_introduction

from .extensions import config, log_db, paper_db, profile_db, progress_db


def run_engine(
    url: str,
) -> Generator[Tuple[Optional[Progress], Optional[Agent]], None, None]:
    try:
        intro = get_paper_introduction(url)
        if not intro:
            yield None, None
            return

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
                for progress, agent in run_result:
                    yield progress, agent
                    engine.time_step += 1

            engine.transition()
    except Exception as e:
        print(f'Error occurred during engine execution: {e}')

    finally:
        print('Engine execution completed.')
