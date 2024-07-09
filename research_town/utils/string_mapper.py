from beartype.typing import Dict, List, Union


def map_idea_list_to_str(ideas: List[Dict[str, str]]) -> str:
    result = ''
    for i, idea in enumerate(ideas):
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


def map_rebuttal_list_to_str(rebuttals: List[Dict[str, str]]) -> str:
    result = ''
    for rebuttal in rebuttals:
        result += map_rebuttal_to_str(rebuttal)
    return result


def map_paper_to_str(paper: Dict[str, str]) -> str:
    return f"Paper: {paper['abstract']}"


def map_rebuttal_to_str(paper: Dict[str, str]) -> str:
    return f"Rebuttal: {paper['content']}"


def map_review_to_str(review: Dict[str, Union[int, str]]) -> str:
    score = review['score']
    summary = review['summary']
    strength = review['strength']
    weakness = review['weakness']
    return f'Score: {score}\nSummary: {summary}\nStrength: {strength}\nWeakness: {weakness}'


def map_meta_review_to_str(meta_review: Dict[str, str]) -> str:
    decision = meta_review['decision']
    summary = meta_review['summary']
    strength = meta_review['strength']
    weakness = meta_review['weakness']
    return f'Summary: {summary}\nStrength: {strength}\nWeakness: {weakness}\nDecision: {decision}'


def map_meta_review_list_to_str(meta_reviews: List[Dict[str, str]]) -> str:
    result = ''
    for meta_review in meta_reviews:
        result += map_meta_review_to_str(meta_review)
    return result


def map_insights_to_str(insights: List[Dict[str, str]]) -> str:
    result = ''
    for insight in insights:
        result += map_insight_to_str(insight)
    return result


def map_insight_to_str(insight: Dict[str, str]) -> str:
    return f"{insight['content']}"
