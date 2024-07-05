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
    agent_db = AgentProfileDB()
    agent_db.fetch_and_add_agents(
        initial_list=["Jiaxuan You", "Jure Leskovec"])
    agent_db.save_to_file("./trial/agent_gnn.json")
    # paper_db = PaperProfileDB()
    # env_db = EnvLogDB()
    # progress_db = ProgressDB()
    # config = Config(config_file_path)
    # paper_submission_env = PaperSubmissionMultiAgentEnvironment(
    #     agent_profiles=agent_profiles,
    #     agent_roles=role_list,
    #     agent_db=agent_db,
    #     paper_db=paper_db,
    #     env_db=env_db,
    #     progress_db=progress_db,
    #     config=config,
    # )
    # paper_rebuttal_env = PeerReviewMultiAgentEnv(
    #     agent_profiles=agent_profiles,
    #     agent_roles=role_list,
    #     agent_db=agent_db,
    #     paper_db=paper_db,
    #     env_db=env_db,
    #     progress_db=progress_db,
    #     config=config,
    # )

    # # Paper Submission
    # submission_done = False
    # while not submission_done:
    #     paper_submission_env.step()
    #     submission_done = paper_submission_env.terminated
    # paper = paper_submission_env.paper

    # # Paper Review
    # paper_rebuttal_env.initialize_submission(paper)
    # rebuttal_done = False
    # while not rebuttal_done:
    #     paper_rebuttal_env.step()
    #     rebuttal_done = paper_rebuttal_env.terminated


def main() -> None:
    run_sync_experiment(
        agent_list=['Jiaxuan You', 'Jure Leskovec'],
        role_list=['proj_leader', 'reviewer'],
        config_file_path='./configs/default_config.yaml',
    )


if __name__ == '__main__':
    main()
