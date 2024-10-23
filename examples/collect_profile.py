from typing import List

from research_town.configs import Config
from research_town.dbs import ProfileDB


def collect_profile(names: List[str], config: Config) -> None:
    db = ProfileDB(config=config.database)
    for name in names:
        db.pull_profiles(names=[name], config=config)


if __name__ == '__main__':
    names = ['Jiaxuan You']
    config = Config('../configs')
    collect_profile(names, config)
