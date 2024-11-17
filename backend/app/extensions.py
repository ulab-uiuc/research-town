from research_town.configs import Config
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB

config_file_path = 'configs'
config = Config(config_file_path)

profile_db = ProfileDB(config.database)
paper_db = PaperDB(config.database)
log_db = LogDB(config.database)
progress_db = ProgressDB(config.database)
