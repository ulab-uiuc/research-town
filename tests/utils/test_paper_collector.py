import datetime
from unittest.mock import MagicMock, patch

from research_town.data import Profile
from research_town.utils.paper_collector import (
    get_paper_by_arxiv_id,
    get_paper_by_keyword,
    get_paper_content_from_html,
    get_paper_introduction,
    get_recent_papers,
    get_references,
    get_related_papers,
    process_paper,
)


@patch('arxiv.Client')
def test_get_recent_paper(mock_client: MagicMock) -> None:
    # Create mock client instance and configure mock papers
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance

    # Mock paper data
    mock_paper_1 = MagicMock()
    mock_paper_1.title = 'Paper 1'
    mock_paper_1.entry_id = 'http://example.com/1'
    mock_paper_1.summary = 'Summary 1'
    mock_paper_1.primary_category = 'cs'
    mock_paper_1.published = datetime.datetime(2023, 7, 1)

    mock_paper_2 = MagicMock()
    mock_paper_2.title = 'Paper 2'
    mock_paper_2.entry_id = 'http://example.com/2'
    mock_paper_2.summary = 'Summary 2'
    mock_paper_2.primary_category = 'cs'
    mock_paper_2.published = datetime.datetime(2023, 7, 2)

    # Set return value for client.results
    mock_client_instance.results.return_value = [mock_paper_1, mock_paper_2]

    # Call the function you're testing
    result_papers = get_recent_papers(max_results=2, domain='cs.AI')

    # Assertions
    assert len(result_papers) == 2
    assert result_papers[0].title == 'Paper 1'
    assert result_papers[1].title == 'Paper 2'
    assert result_papers[0].url == 'http://example.com/1'
    assert result_papers[1].url == 'http://example.com/2'

    # Check if mock client was called
    mock_client.assert_called_once()


@patch('arxiv.Client')
def test_get_related_papers(mock_client: MagicMock) -> None:
    # Create mock client instance and configure mock papers
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance

    # Mock paper data
    mock_paper_1 = MagicMock()
    mock_paper_1.title = 'Paper 1'
    mock_paper_1.entry_id = 'http://example.com/1'
    mock_paper_1.summary = 'Summary 1'
    mock_paper_1.primary_category = 'cs'
    mock_paper_1.published = datetime.datetime(2023, 7, 1)

    mock_paper_2 = MagicMock()
    mock_paper_2.title = 'Paper 2'
    mock_paper_2.entry_id = 'http://example.com/2'
    mock_paper_2.summary = 'Summary 2'
    mock_paper_2.primary_category = 'cs'
    mock_paper_2.published = datetime.datetime(2023, 7, 2)

    # Set return value for client.results
    mock_client_instance.results.return_value = [mock_paper_1, mock_paper_2]

    # Call the function you're testing
    result_papers = get_related_papers(num_results=2, query='test', domain='cs.AI')

    # Assertions
    assert len(result_papers) == 2
    assert result_papers[0].title == 'Paper 1'
    assert result_papers[1].title == 'Paper 2'
    assert result_papers[0].url == 'http://example.com/1'
    assert result_papers[1].url == 'http://example.com/2'

    # Check if mock client was called
    mock_client.assert_called_once()


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
    assert intro1 is not None
    assert intro2 is not None
    assert intro3 is not None

    assert 'Introduction' in intro1
    assert 'Introduction' in intro2
    assert 'Introduction' in intro3


@patch('arxiv.Search')
def test_get_paper_by_arxiv_id(mock_search: MagicMock) -> None:
    # Mock search results
    mock_result = MagicMock()
    mock_result.title = 'Test Paper'
    mock_result.get_short_id.return_value = '1234.5678'

    # Configure the mock search instance
    mock_search_instance = MagicMock()
    mock_search_instance.results.return_value = [mock_result]
    mock_search.return_value = mock_search_instance

    # Call the function
    result = get_paper_by_arxiv_id('1234.5678')

    # Assertions
    assert result is not None
    assert result.title == 'Test Paper'
    mock_search.assert_called_once_with(id_list=['1234.5678'])


@patch('requests.get')
def test_get_references(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'data': [
            {'citedPaper': {'arxivId': '1234.5678', 'title': 'Cited Paper 1'}},
            {'citedPaper': {'arxivId': '2345.6789', 'title': 'Cited Paper 2'}},
        ]
    }
    mock_get.return_value = mock_response

    # Call the function
    references = get_references('1234.5678')

    # Assertions
    assert len(references) == 2
    assert references[0]['arxivId'] == '1234.5678'
    assert references[1]['arxivId'] == '2345.6789'
    mock_get.assert_called_once()


@patch('arxiv.Search')
def test_get_paper_by_keyword(mock_search: MagicMock) -> None:
    # Mock search results
    mock_paper_1 = MagicMock()
    mock_paper_1.get_short_id.return_value = '1234.5678'
    mock_paper_1.title = 'Keyword Paper 1'

    mock_paper_2 = MagicMock()
    mock_paper_2.get_short_id.return_value = '2345.6789'
    mock_paper_2.title = 'Keyword Paper 2'

    mock_search_instance = MagicMock()
    mock_search_instance.results.return_value = [mock_paper_1, mock_paper_2]
    mock_search.return_value = mock_search_instance

    # Call the function
    papers = get_paper_by_keyword('machine learning', set(), max_papers=2)

    # Assertions
    assert len(papers) == 2
    assert papers[0].title == 'Keyword Paper 1'
    assert papers[1].title == 'Keyword Paper 2'
    mock_search.assert_called_once()


@patch('research_town.utils.paper_collector.get_references')
def test_process_paper(mock_get_references: MagicMock) -> None:
    # Mock references
    mock_get_references.return_value = [
        {'arxivId': '2345.6789', 'title': 'Cited Paper 1'}
    ]

    # Mock arxiv paper
    mock_paper = MagicMock()
    mock_paper.title = 'Test Paper'
    mock_paper.get_short_id.return_value = '1234.5678'
    mock_paper.authors = [Profile(name='Author 1')]
    mock_paper.summary = 'This is a test summary.'
    mock_paper.published = MagicMock()
    mock_paper.updated = MagicMock()
    mock_paper.published.isoformat.return_value = '2023-07-01T00:00:00'
    mock_paper.updated.isoformat.return_value = '2023-07-02T00:00:00'

    # Call the function
    result = process_paper(mock_paper)

    # Assertions
    assert result['title'] == 'Test Paper'
    assert result['arxiv_id'] == '1234.5678'
    assert result['authors'][0].name == 'Author 1'
    assert result['abstract'] == 'This is a test summary.'
    assert result['references'] == [{'arxivId': '2345.6789', 'title': 'Cited Paper 1'}]
    mock_get_references.assert_called_once_with('1234.5678')
