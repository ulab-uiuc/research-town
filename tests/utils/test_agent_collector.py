from research_town.utils.agent_collector import (
    co_author_filter,
    co_author_frequency,
    fetch_author_info,
)


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
