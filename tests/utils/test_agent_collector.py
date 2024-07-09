from unittest.mock import MagicMock, patch

from research_town.utils.agent_collector import (
    author_position,
    bfs,
    co_author_filter,
    co_author_frequency,
    fetch_author_info,
    get_authors,
)


def test_get_authors() -> None:
    authors = ['Alice', 'Bob', 'Charlie']
    assert get_authors(authors) == 'Alice, Bob, Charlie'
    assert get_authors(authors, first_author=True) == 'Alice'


def test_author_position() -> None:
    author_list = ['Alice', 'Bob', 'Charlie']
    assert author_position('Bob', author_list) == 2
    assert author_position('David', author_list) == -1


def test_co_author_frequency() -> None:
    author = 'Alice'
    author_list = ['Alice', 'Bob', 'Charlie', 'Alice']
    co_authors = {'Bob': 1, 'Charlie': 1}
    expected_co_authors = {'Bob': 2, 'Charlie': 2}
    assert co_author_frequency(author, author_list, co_authors) == expected_co_authors


def test_co_author_filter() -> None:
    co_authors = {'Bob': 5, 'Charlie': 3, 'David': 2, 'Eve': 4}
    assert co_author_filter(co_authors, limit=3) == ['Bob', 'Eve', 'Charlie']


def test_fetch_author_info() -> None:
    papers_info, co_author_names = fetch_author_info('Alice')

    assert len(papers_info) > 0
    assert len(papers_info) <= 10
    print(f'Fetched {len(papers_info)} papers.')
    print(f'Co-authors: {co_author_names}')

    assert papers_info[0]['title'] is not None
    assert papers_info[0]['abstract'] is not None
    assert len(co_author_names) > 0


@patch('research_town.utils.agent_collector.fetch_author_info')
def test_bfs(mock_fetch_author_info: MagicMock) -> None:
    mock_fetch_author_info.side_effect = [
        (
            [
                {
                    'title': 'Paper 1',
                    'authors': 'Alice, Bob',
                    'published': '2023-01-01',
                    'updated': '2023-01-02',
                    'primary_cat': 'cs.AI',
                    'cats': ['cs.AI'],
                },
                {
                    'title': 'Paper 2',
                    'authors': 'Alice, Charlie',
                    'published': '2023-01-01',
                    'updated': '2023-01-02',
                    'primary_cat': 'cs.AI',
                    'cats': ['cs.AI'],
                },
            ],
            ['Bob', 'Charlie'],
        ),
        (
            [
                {
                    'title': 'Paper 3',
                    'authors': 'Bob, Alice',
                    'published': '2023-01-01',
                    'updated': '2023-01-02',
                    'primary_cat': 'cs.AI',
                    'cats': ['cs.AI'],
                }
            ],
            ['Alice'],
        ),
        (
            [
                {
                    'title': 'Paper 4',
                    'authors': 'Charlie, Alice',
                    'published': '2023-01-01',
                    'updated': '2023-01-02',
                    'primary_cat': 'cs.AI',
                    'cats': ['cs.AI'],
                }
            ],
            ['Alice'],
        ),
    ]

    graph, node_feat, edge_feat = bfs(['Alice'], node_limit=2)
    assert ('Alice', 'Bob') in graph
    assert ('Alice', 'Charlie') in graph
    assert len(node_feat['Alice']) == 2
    assert len(node_feat['Bob']) == 1
    assert len(node_feat['Charlie']) == 1
