from typing import List

from research_town.configs import Config
from research_town.dbs import ProfileDB


def collect_profile(names: List[str], config: Config, save_path: str) -> None:
    db = ProfileDB()
    for name in names:
        db.pull_profiles(names=[name], config=config)
        db.save_to_json(save_path)
        db.transform_to_embed()
        db.save_to_pkl(save_path)


if __name__ == '__main__':
    names = ['Jiaxuan You']
    config = Config('../configs')
    collect_profile(names, config, './profiles')
