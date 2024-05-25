from unittest.mock import MagicMock, patch

from research_town.envs import (
    PaperRebuttalMultiAgentEnv,
    PaperSubmissionMultiAgentEnvironment,
)

from tests.constants import (
    agent_profile_A,
    agent_profile_B,
    paper_profile_A,
)


@patch("research_town.utils.agent_prompter.model_prompting")
def test_paper_rebuttal_env(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = [
        "Paper Rebuttal Environment."]
    env = PaperRebuttalMultiAgentEnv(
        agent_profiles=[agent_profile_A, agent_profile_B]
    )

    submission = paper_profile_A
    env.initialize_submission(submission)
    env.assign_roles({agent_profile_A.pk: "author",
                      agent_profile_B.pk: "reviewer"})

    while not env.terminated:
        env.step()

    assert isinstance(env.review, list)
    assert len(env.review) > 0
    assert isinstance(env.decision, str)
    assert env.decision in ["accept", "reject", "boarderline"]
    assert isinstance(env.rebuttal, list)
    assert len(env.rebuttal) > 0


@patch("research_town.utils.agent_prompter.model_prompting")
def test_paper_submission_env(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.return_value = ["This is a paper."]

    env = PaperSubmissionMultiAgentEnvironment(
        agent_dict={
            "Jiaxuan You": "Jiaxuan You"
        },
        task={
            "11 May 2024": "Organize a workshop on how far are we from AGI (artificial general intelligence) at ICLR 2024. This workshop aims to become a melting pot for ideas, discussions, and debates regarding our proximity to AGI."
        }
    )
    env.step()
    assert isinstance(env.paper, str)
