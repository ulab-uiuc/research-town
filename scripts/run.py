from typing import Dict

from ..research_town.envs.env_paper_submission import PaperSubmissionMultiAgentEnvironment
from ..research_town.envs.env_paper_rebuttal import PaperRebuttalMultiAgentEnv


def run_sync_experiment(agent_dict: Dict[str, str]):
    # Create Environment and Agents
    paper_submission_env = PaperRebuttalMultiAgentEnv(
        agent_dict=agent_dict)

    paper_rebuttal_env = PaperSubmissionMultiAgentEnvironment(
        agent_dict=agent_dict)

    # Main Event Loop
    submission_done = False
    while not submission_done:
        paper_submission_env.step()
        submission_done = paper_submission_env.terminated
    submission = paper_submission_env.submission

    paper_rebuttal_env.initialize_submission(submission)
    rebuttal_done = False
    while not rebuttal_done:
        paper_rebuttal_env.step()
        rebuttal_done = paper_rebuttal_env.terminated


def main():
    run_sync_experiment(agent_dict={"Jiaxuan You": "Jiaxuan You", "Rex Ying": "Rex Ying",
                                    "Jure Leskovec": "Jure Leskovec", "Christos Faloutsos": "Christos Faloutsos"})


if __name__ == "__main__":
    main()
