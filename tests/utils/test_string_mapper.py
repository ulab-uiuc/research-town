from beartype.typing import Dict, List, Union

from research_town.utils.string_mapper import (
    map_idea_list_to_str,
    map_idea_to_str,
    map_insight_to_str,
    map_insights_to_str,
    map_message_to_str,
    map_paper_list_to_str,
    map_paper_to_str,
    map_rebuttal_to_str,
    map_review_list_to_str,
    map_review_to_str,
)


def test_map_idea_list_to_str() -> None:
    ideas = [{'content': 'Idea 1'}, {'content': 'Idea 2'}, {'content': 'Idea 3'}]
    expected_result = 'Idea 1Idea 2Idea 3'
    assert map_idea_list_to_str(ideas) == expected_result


def test_map_idea_to_str() -> None:
    idea = {'content': 'This is an idea'}
    expected_result = 'This is an idea'
    assert map_idea_to_str(idea) == expected_result


def test_map_paper_list_to_str() -> None:
    papers = [
        {'abstract': 'Abstract 1'},
        {'abstract': 'Abstract 2'},
        {'abstract': 'Abstract 3'},
    ]
    expected_result = 'Paper: Abstract 1Paper: Abstract 2Paper: Abstract 3'
    assert map_paper_list_to_str(papers) == expected_result


def test_map_review_list_to_str() -> None:
    reviews: List[Dict[str, Union[int, str]]] = [
        {'score': 5, 'content': 'Review 1'},
        {'score': 3, 'content': 'Review 2'},
        {'score': 4, 'content': 'Review 3'},
    ]
    expected_result = 'Score: 5\nContent: Review 1Score: 3\nContent: Review 2Score: 4\nContent: Review 3'
    assert map_review_list_to_str(reviews) == expected_result


def test_map_paper_to_str() -> None:
    paper = {'abstract': 'This is a paper abstract'}
    expected_result = 'Paper: This is a paper abstract'
    assert map_paper_to_str(paper) == expected_result


def test_map_rebuttal_to_str() -> None:
    rebuttal = {'content': 'This is a rebuttal'}
    expected_result = 'Rebuttal: This is a rebuttal'
    assert map_rebuttal_to_str(rebuttal) == expected_result


def test_map_review_to_str() -> None:
    review: Dict[str, Union[int, str]] = {'score': 4, 'content': 'This is a review'}
    expected_result = 'Score: 4\nContent: This is a review'
    assert map_review_to_str(review) == expected_result


def test_map_message_to_str() -> None:
    message = {'agent_from_name': 'Alice', 'agent_to_name': 'Bob'}
    expected_result = 'Message from Alice to Bob\n'
    assert map_message_to_str(message) == expected_result


def test_map_insights_to_str() -> None:
    insights = [
        {'content': 'Insight 1'},
        {'content': 'Insight 2'},
        {'content': 'Insight 3'},
    ]
    expected_result = 'Insight 1Insight 2Insight 3'
    assert map_insights_to_str(insights) == expected_result


def test_map_insight_to_str() -> None:
    insight = {'content': 'This is an insight'}
    expected_result = 'This is an insight'
    assert map_insight_to_str(insight) == expected_result
