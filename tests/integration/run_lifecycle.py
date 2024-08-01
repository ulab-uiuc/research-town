from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.engines import LifecycleResearchEngine
from tests.mocks.mocking_func import mock_prompting

from ..constants.db_constants import (
    example_agent_db,
    example_env_db,
    example_paper_db,
    example_progress_db,
)


@patch('research_town.utils.agent_prompter.model_prompting')
def test_research_lifecycle_two_stage(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    engine = LifecycleResearchEngine(
        project_name='test',
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        env_db=example_env_db,
        config=Config(),
    )
    engine.enter_state(
        env_name='start', query='Conduct research on Graph Neural Networks (GNN).'
    )
    engine.run()
