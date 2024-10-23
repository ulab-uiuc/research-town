from research_town.configs import Config, DatabaseConfig
from research_town.dbs import LogDB, PaperDB, ProfileDB, ProgressDB


def get_profile_db(database_config: DatabaseConfig) -> ProfileDB:
    db = ProfileDB(config=database_config)
    return db


def get_paper_db(database_config: DatabaseConfig) -> PaperDB:
    db = PaperDB(config=database_config)
    return db


def get_log_db(database_config: DatabaseConfig) -> LogDB:
    db = LogDB(config=database_config)
    return db


def get_progress_db(database_config: DatabaseConfig) -> ProgressDB:
    db = ProgressDB(config=database_config)
    return db


config_file_path = '../configs'
config = Config(config_file_path)

profile_db = get_profile_db(config.database)
paper_db = get_paper_db(config.database)
log_db = get_log_db(config.database)
progress_db = get_progress_db(config.database)
