from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import AgentProfileDB, EnvLogDB, PaperProfileDB, ProgressDB
from research_town.envs import PaperSubmissionMultiAgentEnv, PeerReviewMultiAgentEnv

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


def run_sync_experiment(
    agent_names: List[str],
    agent_roles: List[Role],
    config_file_path: str,
) -> None:
    # Create Environment and Agents
    config = Config(config_file_path)
    agent_db = AgentProfileDB()
    agent_db.pull_agents(agent_names=agent_names, config=config)
    agent_profiles = []
    for _, agent_profile in agent_db.data.items():
        agent_profiles.append(agent_profile)
    paper_db = PaperProfileDB()
    paper_db.pull_papers(num=10, domain='graph neural networks')
    env_db = EnvLogDB()
    progress_db = ProgressDB()
    config = Config(config_file_path)
    paper_submission_env = PaperSubmissionMultiAgentEnv(
        agent_profiles=agent_profiles,
        agent_roles=agent_roles,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )
    peer_review_env = PeerReviewMultiAgentEnv(
        agent_profiles=agent_profiles,
        agent_roles=agent_roles,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )

    # Paper Submission
    paper = paper_submission_env.run()

    # Paper Review
    peer_review_env.run(paper)


def main() -> None:
    run_sync_experiment(
        agent_names=['Jiaxuan You', 'Jure Leskovec'],
        agent_roles=['proj_leader', 'reviewer'],
        config_file_path='./configs/default_config.yaml',
    )


if __name__ == '__main__':
    main()
