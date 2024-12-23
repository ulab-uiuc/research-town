from beartype.typing import Dict, List, Union


def map_idea_list_to_str(ideas: List[Dict[str, str]]) -> str:
    result = ''
    for i, idea in enumerate(ideas):
        result += f'{i+1}th idea: ' + map_idea_to_str(idea) + '\n'
    return result


def map_idea_to_str(idea: Dict[str, str]) -> str:
    assert 'content' in idea
    return f"{idea['content']}"


def map_proposal_to_str(paper: Dict[str, str]) -> str:
    assert 'content' in paper
    return f"{paper['content']}"

def map_cited_abstracts_to_str(abstracts: List[str]) -> str:
    result = ''
    for i, abstract in enumerate(abstracts):
        result += f'{i+1}th cited abstract: ' + abstract + '\n'
    return result

def map_paper_list_to_str(papers: List[Dict[str, str]]) -> str:
    result = ''
    for i, paper in enumerate(papers):
        result += f'{i+1}th paper: ' + map_paper_to_str(paper) + '\n'
    return result


def map_paper_to_str(paper: Dict[str, str]) -> str:
    assert 'abstract' in paper
    return f"{paper['abstract']}"


def map_review_list_to_str(reviews: List[Dict[str, Union[int, str]]]) -> str:
    result = ''
    for review in reviews:
        result += map_review_to_str(review)
    return result


def map_review_to_str(review: Dict[str, Union[int, str]]) -> str:
    assert 'score' in review
    # assert 'summary' in review
    assert 'strength' in review
    assert 'weakness' in review
    score = review['score']
    # summary = review['summary']
    strength = review['strength']
    weakness = review['weakness']
    return f'Score: {score}\nStrength: {strength}\nWeakness: {weakness}\n\n'


def map_rebuttal_list_to_str(rebuttals: List[Dict[str, str]]) -> str:
    result = ''
    for rebuttal in rebuttals:
        result += map_rebuttal_to_str(rebuttal)
    return result


def map_rebuttal_to_str(rebuttal: Dict[str, str]) -> str:
    assert 'content' in rebuttal
    return f"{rebuttal['content']}"


def map_metareview_list_to_str(metareviews: List[Dict[str, str]]) -> str:
    result = ''
    for metareview in metareviews:
        result += map_metareview_to_str(metareview)
    return result


def map_metareview_to_str(metareview: Dict[str, str]) -> str:
    assert 'decision' in metareview
    assert 'summary' in metareview
    assert 'strength' in metareview
    assert 'weakness' in metareview
    decision = metareview['decision']
    summary = metareview['summary']
    strength = metareview['strength']
    weakness = metareview['weakness']
    return f'Summary: {summary}\nStrength: {strength}\nWeakness: {weakness}\nDecision: {decision}'


def map_insight_list_to_str(insights: List[Dict[str, str]]) -> str:
    result = ''
    for i, insight in enumerate(insights):
        result += f'{i+1}th insight: ' + map_insight_to_str(insight) + '\n'
    return result


def map_insight_to_str(insight: Dict[str, str]) -> str:
    assert 'content' in insight
    return f"{insight['content']}"
