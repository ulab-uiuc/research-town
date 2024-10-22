import os

from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB

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
