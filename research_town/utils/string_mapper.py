from beartype.typing import Dict, List, Union


def map_idea_list_to_str(ideas: List[Dict[str, str]]) -> str:
    result = ''
    for idea in ideas:
        result += map_idea_to_str(idea)
    return result


def map_idea_to_str(idea: Dict[str, str]) -> str:
    return f"{idea['content']}"


def map_paper_list_to_str(papers: List[Dict[str, str]]) -> str:
    result = ''
    for paper in papers:
        result += map_paper_to_str(paper)
    return result


def map_review_list_to_str(reviews: List[Dict[str, Union[int, str]]]) -> str:
    result = ''
    for review in reviews:
        result += map_review_to_str(review)
    return result


def map_paper_to_str(paper: Dict[str, str]) -> str:
    return f"Title: {paper['title']}\nAbstract: {paper['abstract']}"


def map_review_to_str(review: Dict[str, Union[int, str]]) -> str:
    score = review['review_score']
    content = review['review_content']
    return f'Score: {score}\nContent: {content}'


def map_message_to_str(message: Dict[str, str]) -> str:
    return f"Message from {message['agent_from_name']} to {message['agent_to_name']}\n"

def map_insights_to_str(insights: List[Dict[str, str]]) -> str:
    result = ''
    for insight in insights:
        result += map_insight_to_str(insight)
    return result

def map_insight_to_str(insight: Dict[str, str]) -> str:
    return f"{insight['content']}"