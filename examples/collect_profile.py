from research_town.dbs import ProfileDB
from research_town.configs import Config
from typing import List


def collect_profile(names: List[str], config: Config, save_path: str):
    db = ProfileDB()
    for name in names:
        db.pull_profiles(names=[name], config=config)
        db.save_to_json(save_path)

if __name__ == '__main__':
    names = ["Jiaxuan You"]
    config = Config('../configs')
    collect_profile(names, config, './profiles')