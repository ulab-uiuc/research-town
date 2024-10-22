from research_town.utils.profile_collector import (
    coauthor_filter,
    coauthor_frequency,
    collect_publications_and_coauthors,
)


def test_coauthor_frequency() -> None:
    author = 'Alice'
    author_list = ['Alice', 'Bob', 'Charlie', 'Alice']
    co_authors = {'Bob': 1, 'Charlie': 1}
    expected_co_authors = {'Bob': 2, 'Charlie': 2}
    assert coauthor_frequency(author, author_list, co_authors) == expected_co_authors


def test_coauthor_filter() -> None:
    co_authors = {'Bob': 5, 'Charlie': 3, 'David': 2, 'Eve': 4}
    assert coauthor_filter(co_authors, limit=3) == ['Bob', 'Eve', 'Charlie']


def test_collect_publications_and_coauthors() -> None:
    publications, titles, co_author_names = collect_publications_and_coauthors('Rex Ying')

    assert len(publications) > 0
    assert len(publications) <= 10
    for publication in publications:
        assert publication is not None

    assert len(co_author_names) > 0
