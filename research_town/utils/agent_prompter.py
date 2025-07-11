import re

from beartype import beartype
from beartype.typing import Dict, List, Optional, Tuple, Union
from litellm.utils import token_counter

from .model_prompting import model_prompting
from .prompt_constructor import openai_format_prompt_construct
from .string_mapper import (
    map_cited_abstracts_to_str,
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
    contexts: List[str],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    papers: Optional[List[Dict[str, str]]] = None,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[str, List[str], str, list[dict[str, str]]]:
    papers_str = map_paper_list_to_str(papers) if papers else 'No papers provided.\n'
    template_input = {
        'bio': profile['bio'],
        'contexts': contexts,
        'papers': papers_str,
    }
    messages = openai_format_prompt_construct(prompt_template, template_input)

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
    return summary, keywords, valuable_points, messages


@beartype
def brainstorm_idea_prompting(
    bio: str,
    insights: List[Dict[str, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    papers: Optional[List[Dict[str, str]]] = None,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[List[str], List[Dict[str, str]]]:
    insights_str = map_insight_list_to_str(insights)
    papers_str = map_paper_list_to_str(papers) if papers else 'No papers provided.\n'
    template_input = {'bio': bio, 'insights': insights_str, 'papers': papers_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    return model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    ), messages


@beartype
def summarize_idea_prompting(
    contexts: List[str],
    ideas: List[Dict[str, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[List[str], List[Dict[str, str]]]:
    ideas_str = map_idea_list_to_str(ideas)
    template_input = {'ideas': ideas_str, 'contexts': contexts}
    messages = openai_format_prompt_construct(prompt_template, template_input)

    return model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    ), messages


@beartype
def write_proposal_prompting(
    idea: Dict[str, str],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    papers: Optional[List[Dict[str, str]]] = None,
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[str, Dict[str, str], List[Dict[str, str]]]:
    idea_str = map_idea_to_str(idea)
    papers_str = map_paper_list_to_str(papers) if papers else 'No papers provided.\n'
    template_input = {'idea': idea_str, 'papers': papers_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)

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

    return proposal, q5_result, messages


@beartype
def write_review_prompting(
    proposal: Dict[str, str],
    model_name: str,
    profile: Dict[str, str],
    strength_prompt_template: Dict[str, Union[str, List[str]]],
    weakness_prompt_template: Dict[str, Union[str, List[str]]],
    score_prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[
    str,
    str,
    int,
    List[Dict[str, str]],
    List[Dict[str, str]],
    List[Dict[str, str]],
]:
    token_input_count = 0
    token_output_count = 0
    proposal_str = map_proposal_to_str(proposal)

    citations: Union[str, List[str]] = proposal.get('citations', [])
    assert isinstance(citations, list)
    citations_str = map_cited_abstracts_to_str(citations)

    strength_template_input = {
        'proposal': proposal_str,
        'bio': profile['bio'],
        'citations': citations_str,
    }
    strength_messages = openai_format_prompt_construct(
        strength_prompt_template, strength_template_input
    )
    weakness_template_input = {
        'proposal': proposal_str,
        'bio': profile['bio'],
        'citations': citations_str,
    }
    weakness_messages = openai_format_prompt_construct(
        weakness_prompt_template, weakness_template_input
    )

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

    token_input_count += token_counter(model=model_name, messages=strength_messages)
    token_input_count += token_counter(model=model_name, messages=weakness_messages)
    token_output_count += token_counter(model=model_name, text=strength)
    token_output_count += token_counter(model=model_name, text=weakness)

    score_template_input = {
        'strength': strength,
        'weakness': weakness,
        'bio': profile['bio'],
    }
    score_messages = openai_format_prompt_construct(
        score_prompt_template, score_template_input
    )

    score_response_str = model_prompting(
        model_name,
        score_messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )[0]

    token_input_count += token_counter(model=model_name, messages=score_messages)
    token_output_count += token_counter(model=model_name, text=score_response_str)

    # find the first number in 10, 1, 2, 3, 4, 5, 6, 7, 8, 9
    score_str = re.findall(r'\d+', score_response_str)
    score_str_1st = score_str[0] if score_str else 0
    score = int(score_str_1st)

    print(f'Token input count: {token_input_count}')
    print(f'Token output count: {token_output_count}')

    return (
        strength,
        weakness,
        score,
        strength_messages,
        weakness_messages,
        score_messages,
    )


@beartype
def write_metareview_prompting(
    reviews: List[Dict[str, Union[int, str]]],
    model_name: str,
    strength_prompt_template: Dict[str, Union[str, List[str]]],
    weakness_prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> Tuple[
    str,
    str,
    List[Dict[str, str]],
    List[Dict[str, str]],
]:
    token_input_count = 0
    token_output_count = 0

    reviews_str = map_review_list_to_str(reviews)
    strength_template_input = {
        'reviews': reviews_str,
    }
    weakness_template_input = {
        'reviews': reviews_str,
    }
    strength_messages = openai_format_prompt_construct(
        strength_prompt_template, strength_template_input
    )
    weakness_messages = openai_format_prompt_construct(
        weakness_prompt_template, weakness_template_input
    )
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
    token_input_count += token_counter(model=model_name, messages=strength_messages)
    token_input_count += token_counter(model=model_name, messages=weakness_messages)
    token_output_count += token_counter(model=model_name, text=strength)
    token_output_count += token_counter(model=model_name, text=weakness)

    return (
        strength,
        weakness,
        strength_messages,
        weakness_messages,
    )


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
) -> Tuple[str, Dict[str, str], List[Dict[str, str]]]:
    proposal_str = map_proposal_to_str(proposal)
    review_str = map_review_to_str(review)
    template_input = {'proposal': proposal_str, 'review': review_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
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

    return rebuttal, q5_result, messages
