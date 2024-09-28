import datetime
from unittest.mock import MagicMock, patch

from research_town.utils.paper_collector import (
    get_daily_papers,
    get_paper_content_from_html,
    get_paper_introduction,
)


def test_get_daily_papers() -> None:
    with patch('arxiv.Client') as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        mock_paper_1 = MagicMock()
        mock_paper_1.title = 'Paper 1'
        mock_paper_1.entry_id = 'http://example.com/1'
        mock_paper_1.summary = 'Summary 1'
        mock_paper_1.published = datetime.datetime(2023, 7, 1)

        mock_paper_2 = MagicMock()
        mock_paper_2.title = 'Paper 2'
        mock_paper_2.entry_id = 'http://example.com/2'
        mock_paper_2.summary = 'Summary 2'
        mock_paper_2.published = datetime.datetime(2023, 7, 2)

        mock_client_instance.results.return_value = [mock_paper_1, mock_paper_2]

        result, newest_day = get_daily_papers('test_topic')

        assert len(result) == 2
        assert newest_day == datetime.date(2023, 7, 2)  # Compare to the date part only


def test_get_paper_content_from_html() -> None:
    sections = get_paper_content_from_html('https://arxiv.org/html/2403.05534v1')
    assert sections is not None
    assert '1 Introduction' in sections
    assert len(sections['1 Introduction']) > 0

def test_get_paper_introduction() -> None:
    test_url1 = 'https://arxiv.org/pdf/2409.16928'
    test_url2 = 'https://openreview.net/pdf?id=NnMEadcdyD'
    test_url3 = 'https://arxiv.org/abs/2409.17012'
    intro1 = get_paper_introduction(test_url1)
    intro2 = get_paper_introduction(test_url2)
    intro3 = get_paper_introduction(test_url3)
    assert(intro1 is not None)
    assert(intro2 is not None)
    assert(intro3 is not None)
    
    assert('Introduction' in intro1)
    assert('Introduction' in intro2)
    assert('Introduction' in intro3)