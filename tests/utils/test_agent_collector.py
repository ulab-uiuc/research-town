from research_town.utils.agent_collector import (
    coauthor_filter,
    coauthor_frequency,
    collect_paper_abstracts_and_coauthors,
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


def test_collect_paper_abstracts_and_coauthors() -> None:
    paper_abstracts, co_author_names = collect_paper_abstracts_and_coauthors('Alice')

    assert len(paper_abstracts) > 0
    assert len(paper_abstracts) <= 10
    for paper_abstract in paper_abstracts:
        assert paper_abstract is not None

    assert len(co_author_names) > 0
