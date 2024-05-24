from unittest.mock import MagicMock, patch

from research_town.envs.env_paper_rebuttal import (
    PaperRebuttalMultiAgentEnv,
)
from tests.constants import (
    agent_profile_A,
    agent_profile_B,
    paper_profile,
)


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_paper_rebuttal_env(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "Paper Rebuttal Environment."]
    env = PaperRebuttalMultiAgentEnv(agent_dict={agent_profile_A.agent_id: agent_profile_A.name,
                                                 agent_profile_B.agent_id: agent_profile_B.name})

    submission = paper_profile
    env.initialize_submission(submission)
    env.assign_roles({agent_profile_A.name: "author",
                      agent_profile_B.name: "reviewer"})

    while not env.terminated:
        env.step()

    assert isinstance(env.review, list)
    assert len(env.review) > 0
    assert isinstance(env.decision, str)
    assert env.decision in ["accept", "reject", "boarderline"]
    assert isinstance(env.rebuttal, list)
    assert len(env.rebuttal) > 0
