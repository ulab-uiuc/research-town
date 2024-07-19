from beartype import beartype
from beartype.typing import Dict, List, Optional, Union

from .model_prompting import model_prompting
from .string_mapper import (
    map_idea_to_str,
    map_insight_list_to_str,
    map_insight_to_str,
    map_meta_review_to_str,
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
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    prompt_template: Optional[str] = None,
) -> str:
    input_data = {'insight': map_insight_to_str(insight)}
    prompt = prompt_template.format_map(input_data)
    insight_eval = model_prompting(
        model_name,
        prompt,
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
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    prompt_template: Optional[str] = None,
) -> str:
    input_data = {
        'idea': map_idea_to_str(idea),
        'insights': map_insight_list_to_str(insights),
    }
    prompt = prompt_template.format_map(input_data)
    idea_eval = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return idea_eval


@beartype
def research_paper_submission_quality_eval_prompting(
    model_name: str,
    insights: List[Dict[str, str]],
    idea: Dict[str, str],
    paper: Dict[str, str],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    prompt_template: Optional[str] = None,
) -> str:
    input_data = {
        'insights': map_insight_list_to_str(insights),
        'idea': map_idea_to_str(idea),
        'paper': map_paper_to_str(paper),
    }
    prompt = prompt_template.format_map(input_data)
    paper_eval = model_prompting(
        model_name,
        prompt,
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
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    prompt_template: Optional[str] = None,
) -> str:
    input_data = {
        'idea': map_idea_to_str(idea),
        'insights': map_insight_list_to_str(insights),
        'paper': map_paper_to_str(paper),
        'review': map_review_to_str(review),
    }
    prompt = prompt_template.format_map(input_data)
    review_eval = model_prompting(
        model_name,
        prompt,
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
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    prompt_template: Optional[str] = None,
) -> str:
    input_data = {
        'idea': map_idea_to_str(idea),
        'insights': map_insight_list_to_str(insights),
        'paper': map_paper_to_str(paper),
        'review': map_review_to_str(review),
        'rebuttal': map_rebuttal_to_str(rebuttal),
    }
    prompt = prompt_template.format_map(input_data)
    rebuttal_eval = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return rebuttal_eval


def research_meta_review_quality_eval_prompting(
    model_name: str,
    insights: List[Dict[str, str]],
    idea: Dict[str, str],
    paper: Dict[str, str],
    reviews: List[Dict[str, Union[int, str]]],
    rebuttals: List[Dict[str, str]],
    meta_review: Dict[str, str],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
    prompt_template: Optional[str] = None,
) -> str:
    input_data = {
        'insights': map_insight_list_to_str(insights),
        'idea': map_idea_to_str(idea),
        'paper': map_paper_to_str(paper),
        'reviews': map_review_list_to_str(reviews),
        'rebuttals': map_rebuttal_list_to_str(rebuttals),
        'meta_review': map_meta_review_to_str(meta_review),
    }
    prompt = prompt_template.format_map(input_data)
    meta_review_eval = model_prompting(
        model_name,
        prompt,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )[0]
    return meta_review_eval
