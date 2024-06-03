from beartype.typing import Dict, List

from research_town.configs import Config
from research_town.dbs import AgentProfile, AgentProfileDB, EnvLogDB, PaperProfileDB
from research_town.envs import (
    PaperRebuttalMultiAgentEnv,
    PaperSubmissionMultiAgentEnvironment,
)


def run_sync_experiment(
    agent_list: List[str],
    role_list: List[str],
    task: Dict[str, str],
    config_file_path: str,
) -> None:
    # Create Environment and Agents
    agent_profiles = [
        AgentProfile(name=agent, bio='A researcher in machine learning.')
        for agent in agent_list
    ]
    agent_db = AgentProfileDB()
    paper_db = PaperProfileDB()
    env_db = EnvLogDB()
    config = Config(config_file_path)
    paper_submission_env = PaperSubmissionMultiAgentEnvironment(
        agent_profiles=agent_profiles,
        task=task,
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
    role_dict = {}
    for agent_profile, role in zip(agent_profiles, role_list):
        role_dict[agent_profile.pk] = role
    paper_rebuttal_env.assign_roles(role_dict=role_dict)
    rebuttal_done = False
    while not rebuttal_done:
        paper_rebuttal_env.step()
        rebuttal_done = paper_rebuttal_env.terminated


def main() -> None:
    run_sync_experiment(
        agent_list=['Jiaxuan You', 'Jure Leskovec'],
        role_list=['author', 'reviewer'],
        task={},
        config_file_path='./configs/default_config.yaml',
    )


if __name__ == '__main__':
    main()
