import re

from beartype import beartype
from beartype.typing import Dict, List, Optional, Tuple, Union

from .model_prompting import model_prompting
from .prompt_constructor import openai_format_prompt_construct, save_prompt_to_json
from .string_mapper import (
    map_idea_list_to_str,
    map_idea_to_str,
    map_insight_list_to_str,
    map_paper_list_to_str,
    map_proposal_to_str,
    map_review_list_to_str,
    map_review_to_str,
)


@beartype
def review_literature_prompting(
    profile: Dict[str, str],
    papers: List[Dict[str, str]],
    contexts: List[str],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[str, List[str], str]:
    papers_str = map_paper_list_to_str(papers)
    template_input = {
        'bio': profile['bio'],
        'contexts': contexts,
        'papers': papers_str,
    }
    messages = openai_format_prompt_construct(prompt_template, template_input)
    save_prompt_to_json('review_literature', messages[0]['content'])

    insight = model_prompting(
        model_name,
        messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]

    summary_pattern = r'Summary of Target Paper:(.*?)Keywords of Target Paper:'
    keywords_pattern = (
        r'Keywords of Target Paper:(.*?)Valuable Points from Target Paper:'
    )
    valuable_points_pattern = r'Valuable Points from Target Paper:(.*)'

    summary_match = re.search(summary_pattern, insight, re.DOTALL)
    keywords_match = re.search(keywords_pattern, insight, re.DOTALL)
    valuable_points_match = re.search(valuable_points_pattern, insight, re.DOTALL)

    summary = summary_match.group(1).strip() if summary_match else ''
    keywords = keywords_match.group(1).strip() if keywords_match else ''
    keywords = keywords.split(',')
    keywords = [keyword.strip() for keyword in keywords]
    valuable_points = (
        valuable_points_match.group(1).strip() if valuable_points_match else ''
    )
    return summary, keywords, valuable_points


@beartype
def brainstorm_idea_prompting(
    bio: str,
    insights: List[Dict[str, str]],
    papers: List[Dict[str, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    insights_str = map_insight_list_to_str(insights)
    papers_str = map_paper_list_to_str(papers)
    template_input = {'bio': bio, 'insights': insights_str, 'papers': papers_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    save_prompt_to_json('brainstorm_idea', messages[0]['content'])
    return model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )


@beartype
def discuss_idea_prompting(
    bio: str,
    contexts: List[str],
    ideas: List[Dict[str, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    ideas_str = map_idea_list_to_str(ideas)
    template_input = {'bio': bio, 'ideas': ideas_str, 'contexts': contexts}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    save_prompt_to_json('discuss_idea', messages[0]['content'])
    return model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )


@beartype
def write_proposal_prompting(
    idea: Dict[str, str],
    papers: List[Dict[str, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[str, Dict[str, str]]:
    idea_str = map_idea_to_str(idea)
    papers_str = map_paper_list_to_str(papers)
    template_input = {'idea': idea_str, 'papers': papers_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    save_prompt_to_json('write_proposal', messages[0]['content'])
    proposal = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]

    pattern = r'\[Question (\d+)\](.*?)(?=\[Question \d+\]|\Z)'
    matches = re.findall(pattern, proposal, re.DOTALL)
    q5_result = {}

    for match in matches:
        question_number = f'q{match[0]}'
        answer = match[1].strip()
        q5_result[question_number] = answer

    return proposal, q5_result


@beartype
def write_review_prompting(
    proposal: Dict[str, str],
    model_name: str,
    summary_prompt_template: Dict[str, Union[str, List[str]]],
    strength_prompt_template: Dict[str, Union[str, List[str]]],
    weakness_prompt_template: Dict[str, Union[str, List[str]]],
    ethical_prompt_template: Dict[str, Union[str, List[str]]],
    score_prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[str, str, str, str, int]:
    proposal_str = map_proposal_to_str(proposal)
    summary_template_input = {'proposal': proposal_str}
    summary_messages = openai_format_prompt_construct(
        summary_prompt_template, summary_template_input
    )
    summary = model_prompting(
        model_name,
        summary_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]

    strength_template_input = {'proposal': proposal_str, 'summary': summary}
    strength_messages = openai_format_prompt_construct(
        strength_prompt_template, strength_template_input
    )
    save_prompt_to_json('review_strength', strength_messages[0]['content'])
    weakness_template_input = {'proposal': proposal_str, 'summary': summary}
    weakness_messages = openai_format_prompt_construct(
        weakness_prompt_template, weakness_template_input
    )
    save_prompt_to_json('review_weakness', weakness_messages[0]['content'])
    ethical_template_input = {'proposal': proposal_str, 'summary': summary}
    ethical_messages = openai_format_prompt_construct(
        ethical_prompt_template, ethical_template_input
    )
    save_prompt_to_json('review_ethical', ethical_messages[0]['content'])

    strength = model_prompting(
        model_name,
        strength_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]
    weakness = model_prompting(
        model_name,
        weakness_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]
    ethical_concerns = model_prompting(
        model_name,
        ethical_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]

    score_template_input = {
        'proposal': proposal_str,
        'summary': summary,
        'strength': strength,
        'weakness': weakness,
        'ethical_concerns': ethical_concerns,
    }
    score_messages = openai_format_prompt_construct(
        score_prompt_template, score_template_input
    )
    save_prompt_to_json('review_score', score_messages[0]['content'])
    score_str = (
        model_prompting(
            model_name,
            score_messages,
            return_num,
            max_token_num,
            temperature,
            top_p,
            stream,
        )[0]
        .split(
            'Based on the given information, I would give this submission a score of '
        )[1]
        .split(' out of 10')[0]
    )
    score = int(score_str[0]) if score_str[0].isdigit() else 0

    return summary, strength, weakness, ethical_concerns, score


@beartype
def write_metareview_prompting(
    proposal: Dict[str, str],
    reviews: List[Dict[str, Union[int, str]]],
    model_name: str,
    summary_prompt_template: Dict[str, Union[str, List[str]]],
    strength_prompt_template: Dict[str, Union[str, List[str]]],
    weakness_prompt_template: Dict[str, Union[str, List[str]]],
    ethical_prompt_template: Dict[str, Union[str, List[str]]],
    decision_prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[str, str, str, str, bool]:
    proposal_str = map_proposal_to_str(proposal)
    reviews_str = map_review_list_to_str(reviews)
    summary_template_input = {
        'proposal': proposal_str,
        'reviews': reviews_str,
    }
    summary_messages = openai_format_prompt_construct(
        summary_prompt_template, summary_template_input
    )
    save_prompt_to_json('metareview_summary', summary_messages[0]['content'])
    summary = model_prompting(
        model_name,
        summary_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]

    strength_template_input = {
        'proposal': proposal_str,
        'reviews': reviews_str,
        'summary': summary,
    }
    weakness_template_input = {
        'proposal': proposal_str,
        'reviews': reviews_str,
        'summary': summary,
    }
    ethical_template_input = {
        'proposal': proposal_str,
        'reviews': reviews_str,
        'summary': summary,
    }
    strength_messages = openai_format_prompt_construct(
        strength_prompt_template, strength_template_input
    )
    save_prompt_to_json('metareview_strength', strength_messages[0]['content'])
    weakness_messages = openai_format_prompt_construct(
        weakness_prompt_template, weakness_template_input
    )
    save_prompt_to_json('metareview_weakness', weakness_messages[0]['content'])
    ethical_messages = openai_format_prompt_construct(
        ethical_prompt_template, ethical_template_input
    )
    save_prompt_to_json('metareview_ethical', ethical_messages[0]['content'])

    strength = model_prompting(
        model_name,
        strength_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]
    weakness = model_prompting(
        model_name,
        weakness_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]
    ethical_concerns = model_prompting(
        model_name,
        ethical_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]

    decision_template_input = {
        'proposal': proposal_str,
        'reviews': reviews_str,
        'summary': summary,
        'strength': strength,
        'weakness': weakness,
        'ethical_concerns': ethical_concerns,
    }
    decision_messages = openai_format_prompt_construct(
        decision_prompt_template, decision_template_input
    )
    save_prompt_to_json('metareview_decision', decision_messages[0]['content'])
    decision_str = model_prompting(
        model_name,
        decision_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )
    decision = 'accept' in decision_str[0].lower()

    return summary, strength, weakness, ethical_concerns, decision


@beartype
def write_rebuttal_prompting(
    proposal: Dict[str, str],
    review: Dict[str, Union[int, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[str, Dict[str, str]]:
    proposal_str = map_proposal_to_str(proposal)
    review_str = map_review_to_str(review)
    template_input = {'proposal': proposal_str, 'review': review_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    save_prompt_to_json('write_rebuttal', messages[0]['content'])
    rebuttal = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]

    pattern = r'\[Question (\d+)\](.*?)(?=\[Question \d+\]|\Z)'
    matches = re.findall(pattern, rebuttal, re.DOTALL)
    q5_result = {}

    for match in matches:
        question_number = f'q{match[0]}'
        answer = match[1].strip()
        q5_result[question_number] = answer

    return rebuttal, q5_result
