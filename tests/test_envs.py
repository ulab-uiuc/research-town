from unittest.mock import MagicMock, patch

from research_town.envs.env_paper_rebuttal import (
    PaperRebuttalMultiAgentEnv,
)
from tests.constants import (
    agent_profile_A,
    agent_profile_B,
    paper_profile_A,
)


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_paper_rebuttal_env(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
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
