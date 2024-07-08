from beartype.typing import List, Literal

from research_town.configs import Config
from research_town.dbs import (
    AgentProfile,
    AgentProfileDB,
    EnvLogDB,
    PaperProfileDB,
    ProgressDB,
)
from research_town.envs import (
    PaperSubmissionMultiAgentEnvironment,
    PeerReviewMultiAgentEnv,
)

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair'] | None


def run_sync_experiment(
    agent_list: List[str],
    role_list: List[Role],
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
    progress_db = ProgressDB()
    config = Config(config_file_path)
    paper_submission_env = PaperSubmissionMultiAgentEnvironment(
        agent_profiles=agent_profiles,
        agent_roles=role_list,
        agent_db=agent_db,
        paper_db=paper_db,
        env_db=env_db,
        progress_db=progress_db,
        config=config,
    )
    peer_review_env = PeerReviewMultiAgentEnv(
        agent_profiles=agent_profiles,
        agent_roles=role_list,
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
        agent_list=['Jiaxuan You', 'Jure Leskovec'],
        role_list=['proj_leader', 'reviewer'],
        config_file_path='./configs/default_config.yaml',
    )


if __name__ == '__main__':
    main()
