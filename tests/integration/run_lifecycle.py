from unittest.mock import MagicMock, patch

from research_town.configs import Config
from research_town.engines import Engine
from tests.mocks.mocking_func import mock_prompting

from ..constants.db_constants import (
    example_agent_db,
    example_log_db,
    example_paper_db,
    example_progress_db,
)


@patch('research_town.utils.agent_prompter.model_prompting')
def test_research_lifecycle_two_stage(mock_model_prompting: MagicMock) -> None:
    mock_model_prompting.side_effect = mock_prompting

    engine = Engine(
        project_name='test',
        agent_db=example_agent_db,
        paper_db=example_paper_db,
        progress_db=example_progress_db,
        log_db=example_log_db,
        config=Config(),
    )
    engine.run(task='Conduct research on Graph Neural Networks (GNN).')
