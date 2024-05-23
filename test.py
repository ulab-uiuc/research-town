from unittest.mock import MagicMock, patch

from research_town.envs.env_paper_rebuttal import (
    PaperRebuttalMultiAgentEnv,
)
from research_town.envs.env_paper_submission import (
    PaperSubmissionMultiAgentEnvironment,
)

env = PaperSubmissionMultiAgentEnvironment(
    agent_dict={
        "Jiaxuan You": "Jiaxuan You", 
        "Rex Ying": "Rex Ying", 
    },
    task={
        "11 May 2024": "Organize a workshop on how far are we from AGI (artificial general intelligence) at ICLR 2024. This workshop aims to become a melting pot for ideas, discussions, and debates regarding our proximity to AGI."
    }
)
env.step()
assert isinstance(env.paper, str)