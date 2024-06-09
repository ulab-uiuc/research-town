from beartype.typing import Dict
from research_town_feature.research_town.configs import Config
from research_town_feature.research_town.dbs import AgentProfileDB, EnvLogDB, PaperProfileDB
from research_town_feature.research_town.envs import (
    PaperRebuttalMultiAgentEnv,
    PaperSubmissionMultiAgentEnvironment,
)

def run_sync_experiment(
    configs: Dict[str,str]
) -> None:
    agent_db = AgentProfileDB()
    agent_db.load_from_file("../data/agent_data/" + configs.param.domain)
    agent_profiles = []
    for _, agent_profile in agent_db.data.items():
        agent_profiles.append(agent_profile)
    
    paper_db = PaperProfileDB()
    paper_db.load_from_file("../data/paper_data/" + configs.param.domain)
    paper_profiles = []
    for _, paper_profile in paper_db.data.items():
        paper_profiles.append(paper_profile)
        
    env_db = EnvLogDB()
    paper_submission_env = PaperSubmissionMultiAgentEnvironment(
        agent_profiles=agent_profiles,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        config=configs,
    )
    
    paper_rebuttal_env = PaperRebuttalMultiAgentEnv(
        agent_profiles=agent_profiles,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        config=configs,
    )

    # Paper Submission
    submission_done = False
    while not submission_done:
        paper_submission_env.next_step()
        submission_done = paper_submission_env.terminated
    paper = paper_submission_env.paper
    # Paper Review
    paper_rebuttal_env.initialize_submission(paper)
    paper_rebuttal_env.assign_roles(num=configs.param.reviewer_num)
    rebuttal_done = False
    while not rebuttal_done:
        paper_rebuttal_env.next_step_()
        rebuttal_done = paper_rebuttal_env.terminated



def main() -> None:
    config_file_path='../configs/default_config.yaml'
    config = Config(config_file_path)
    run_sync_experiment(
        configs=config
    )


if __name__ == '__main__':
    main()
