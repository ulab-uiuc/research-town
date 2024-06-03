from research_town.configs import Config
from research_town.dbs import AgentProfileDB, EnvLogDB, PaperProfileDB
from research_town.envs import (
    PaperRebuttalMultiAgentEnv,
    PaperSubmissionMultiAgentEnvironment,
)


def run_sync_experiment(config_file_path: str, domain: str) -> None:
    # Create Environment and Agents

    agent_db = AgentProfileDB()
    agent_db.load_from_file('data/agent_data/' + domain + '.json')
    agent_profiles = []
    for _, agent_profile in agent_db.data.items():
        agent_profiles.append(agent_profile)

    paper_db = PaperProfileDB()
    paper_db.load_from_file('data/paper_data/' + domain + '.json')
    paper_profiles = []
    for _, paper_profile in paper_db.data.items():
        paper_profiles.append(paper_profile)

    env_db = EnvLogDB()
    config = Config(config_file_path)
    paper_submission_env = PaperSubmissionMultiAgentEnvironment(
        agent_profiles=agent_profiles,
        task={},
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        config=config,
    )

    paper_rebuttal_env = PaperRebuttalMultiAgentEnv(
        agent_profiles=agent_profiles,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        config=config,
    )

    # Paper Submission
    submission_done = False
    while not submission_done:
        paper_submission_env.step()
        submission_done = paper_submission_env.terminated
    paper = paper_submission_env.paper

    # Paper Review
    paper_rebuttal_env.initialize_submission(paper)
    paper_rebuttal_env.assign_roles(num=1)
    rebuttal_done = False
    while not rebuttal_done:
        paper_rebuttal_env.step()
        rebuttal_done = paper_rebuttal_env.terminated


def main() -> None:
    run_sync_experiment(
        config_file_path='./configs/default_config.yaml',
        domain='machine_learning_system',
    )


if __name__ == '__main__':
    main()
