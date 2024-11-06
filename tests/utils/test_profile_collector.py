from research_town.utils.profile_collector import (
    coauthor_filter,
    coauthor_frequency,
    collect_publications_and_coauthors,
)


def test_coauthor_frequency() -> None:
    author_id = 'Alice1'
    author_list = [
        {'authorId': 'Alice1', 'name': 'Alice'},
        {'authorId': 'Bob2', 'name': 'Bob'},
        {'authorId': 'Charlie3', 'name': 'Charlie'},
        {'authorId': 'Alice1', 'name': 'Alice'},
    ]
    co_authors = {'Bob': 1, 'Charlie': 1}
    expected_co_authors = {'Bob': 2, 'Charlie': 2}
    assert coauthor_frequency(author_id, author_list, co_authors) == expected_co_authors


def test_coauthor_filter() -> None:
    co_authors = {'Bob': 5, 'Charlie': 3, 'David': 2, 'Eve': 4}
    assert coauthor_filter(co_authors, limit=3) == ['Bob', 'Eve', 'Charlie']


def test_collect_publications_and_coauthors() -> None:
    author = 'Rex Ying'
    known_paper_titles = [
        'GNN Explainer: A Tool for Post-hoc Explanation of Graph Neural Networks'
    ]

    publications, titles, co_author_names = collect_publications_and_coauthors(
        author=author,
        known_paper_titles=known_paper_titles,
        paper_max_num=5,
        exclude_known=True,
    )

    assert isinstance(publications, list)
    assert isinstance(titles, list)
    assert isinstance(co_author_names, list)
    assert len(publications) > 0
    assert len(co_author_names) > 0
