from typing import Dict

from research_town.envs import (
    PaperRebuttalMultiAgentEnv,
    PaperSubmissionMultiAgentEnvironment,
)


def run_sync_experiment(agent_dict: Dict[str, str], task: Dict[str, str]) -> None:
    # Create Environment and Agents
    paper_submission_env = PaperSubmissionMultiAgentEnvironment(
        agent_dict=agent_dict, task=task)
    paper_rebuttal_env = PaperRebuttalMultiAgentEnv(
        agent_dict=agent_dict)

    # Paper Submission
    submission_done = False
    while not submission_done:
        paper_submission_env.step()
        submission_done = paper_submission_env.terminated
    # TODO: rebuild data type
    paper = {"title": paper_submission_env.paper}

    # Paper Review
    paper_rebuttal_env.initialize_submission(paper)
    paper_rebuttal_env.assign_roles(
        {"Jiaxuan You": "author", "Christos Faloutsos": "reviewer"})
    rebuttal_done = False
    while not rebuttal_done:
        paper_rebuttal_env.step()
        rebuttal_done = paper_rebuttal_env.terminated


def main() -> None:
    run_sync_experiment(
        agent_dict={"Jiaxuan You": "Jiaxuan You",
                    "Christos Faloutsos": "Christos Faloutsos"},
        task={
            "11 May 2024": "Organize a workshop on how far are we from AGI (artificial general intelligence) at ICLR 2024. This workshop aims to become a melting pot for ideas, discussions, and debates regarding our proximity to AGI."
        })


if __name__ == "__main__":
    main()
