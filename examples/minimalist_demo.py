from typing import Dict, List

from research_town.dbs import AgentProfile
from research_town.envs import (
    PaperRebuttalMultiAgentEnv,
    PaperSubmissionMultiAgentEnvironment,
)


def run_sync_experiment(agent_list: List[str], role_list: List[str], task: Dict[str, str]) -> None:
    # Create Environment and Agents
    agent_profiles = [AgentProfile(
        name=agent, bio="A researcher in machine learning.") for agent in agent_list]
    paper_submission_env = PaperSubmissionMultiAgentEnvironment(
        agent_profiles=agent_profiles, task=task)
    paper_rebuttal_env = PaperRebuttalMultiAgentEnv(
        agent_profiles=agent_profiles)

    # Paper Submission
    submission_done = False
    while not submission_done:
        paper_submission_env.step()
        submission_done = paper_submission_env.terminated
    paper = paper_submission_env.paper

    # Paper Review
    paper_rebuttal_env.initialize_submission(paper)
    role_dict = {}
    for name, role in zip(agent_list, role_list):
        role_dict[name] = role
    paper_rebuttal_env.assign_roles(role_dict=role_dict)
    rebuttal_done = False
    while not rebuttal_done:
        paper_rebuttal_env.step()
        rebuttal_done = paper_rebuttal_env.terminated


def main() -> None:
    run_sync_experiment(
        agent_list=["Jiaxuan You", "Jure Leskovec"],
        role_list=["author", "reviewer"],
        task={})


if __name__ == "__main__":
    main()
