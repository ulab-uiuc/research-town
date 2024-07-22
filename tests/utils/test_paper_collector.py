import datetime
from unittest.mock import MagicMock, patch

from research_town.utils.paper_collector import get_daily_papers, get_full_content


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


def test_get_full_content() -> None:
    section_contents, table_captions, figure_captions, bibliography = get_full_content(
        'https://arxiv.org/html/2403.05534v1'
    )
    assert section_contents is not None
    assert '\n1 Introduction' in section_contents
    assert len(section_contents['\n1 Introduction']) > 0
    assert table_captions is None
    assert figure_captions is not None
    assert 'Figure 1: ' in figure_captions
    assert len(figure_captions['Figure 1: ']) > 0
    assert bibliography is not None
    assert 'Arora and Huber (2001)' in bibliography
    assert len(bibliography['Arora and Huber (2001)']) > 0
