from beartype import beartype
from beartype.typing import Dict, List, Optional, Union

from .model_prompting import model_prompting
from .prompt_constructor import openai_format_prompt_construct
from .string_mapper import (
    map_idea_to_str,
    map_insight_list_to_str,
    map_insight_to_str,
    map_metareview_to_str,
    map_paper_to_str,
    map_rebuttal_list_to_str,
    map_rebuttal_to_str,
    map_review_list_to_str,
    map_review_to_str,
)


@beartype
def research_insight_quality_eval_prompting(
    model_name: str,
    insight: Dict[str, str],
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    input_data = {'insight': map_insight_to_str(insight)}
    messages = openai_format_prompt_construct(prompt_template, input_data)
    insight_eval = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return insight_eval


@beartype
def research_idea_quality_eval_prompting(
    model_name: str,
    insights: List[Dict[str, str]],
    idea: Dict[str, str],
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    input_data = {
        'idea': map_idea_to_str(idea),
        'insights': map_insight_list_to_str(insights),
    }
    messages = openai_format_prompt_construct(prompt_template, input_data)
    idea_eval = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return idea_eval


@beartype
def research_proposal_quality_eval_prompting(
    model_name: str,
    insights: List[Dict[str, str]],
    idea: Dict[str, str],
    paper: Dict[str, str],
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    input_data = {
        'insights': map_insight_list_to_str(insights),
        'idea': map_idea_to_str(idea),
        'paper': map_paper_to_str(paper),
    }
    messages = openai_format_prompt_construct(prompt_template, input_data)
    paper_eval = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return paper_eval


def research_review_quality_eval_prompting(
    model_name: str,
    insights: List[Dict[str, str]],
    idea: Dict[str, str],
    paper: Dict[str, str],
    review: Dict[str, Union[int, str]],
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    input_data = {
        'idea': map_idea_to_str(idea),
        'insights': map_insight_list_to_str(insights),
        'paper': map_paper_to_str(paper),
        'review': map_review_to_str(review),
    }
    messages = openai_format_prompt_construct(prompt_template, input_data)
    review_eval = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return review_eval


def research_rebuttal_quality_eval_prompting(
    model_name: str,
    insights: List[Dict[str, str]],
    idea: Dict[str, str],
    paper: Dict[str, str],
    review: Dict[str, Union[int, str]],
    rebuttal: Dict[str, str],
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    input_data = {
        'idea': map_idea_to_str(idea),
        'insights': map_insight_list_to_str(insights),
        'paper': map_paper_to_str(paper),
        'review': map_review_to_str(review),
        'rebuttal': map_rebuttal_to_str(rebuttal),
    }
    messages = openai_format_prompt_construct(prompt_template, input_data)
    rebuttal_eval = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return rebuttal_eval


def research_metareview_quality_eval_prompting(
    model_name: str,
    insights: List[Dict[str, str]],
    idea: Dict[str, str],
    paper: Dict[str, str],
    reviews: List[Dict[str, Union[int, str]]],
    rebuttals: List[Dict[str, str]],
    metareview: Dict[str, str],
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> str:
    input_data = {
        'insights': map_insight_list_to_str(insights),
        'idea': map_idea_to_str(idea),
        'paper': map_paper_to_str(paper),
        'reviews': map_review_list_to_str(reviews),
        'rebuttals': map_rebuttal_list_to_str(rebuttals),
        'metareview': map_metareview_to_str(metareview),
    }
    messages = openai_format_prompt_construct(prompt_template, input_data)
    metareview_eval = model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return metareview_eval
