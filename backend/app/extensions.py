from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB

config_file_path = '../configs'

config = Config(config_file_path)
profile_db = ProfileDB(config=config.database)
paper_db = PaperDB(config=config.database)
log_db = LogDB(config=config.database)
progress_db = ProgressDB(config=config.database)

profile_file_path = '../examples/profiles'
paper_file_path = '../examples/papers'
