from beartype import beartype
from beartype.typing import Dict, List, Optional, Tuple, Union

from .model_prompting import model_prompting
from .prompt_constructor import openai_format_prompt_construct
from .string_mapper import (
    map_idea_list_to_str,
    map_idea_to_str,
    map_insight_list_to_str,
    map_paper_list_to_str,
    map_paper_to_str,
    map_rebuttal_list_to_str,
    map_review_list_to_str,
    map_review_to_str,
)


@beartype
def write_bio_prompting(
    publication_info: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    """
    Write bio based on personal research history
    """
    template_input = {'publication_info': publication_info}
    messages = openai_format_prompt_construct(prompt_template, template_input)
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
def review_literature_prompting(
    profile: Dict[str, str],
    papers: List[Dict[str, str]],
    domains: List[str],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    papers_str = map_paper_list_to_str(papers)
    domains_str = '; '.join(domains)
    template_input = {
        'profile_bio': profile['bio'],
        'domains': domains_str,
        'papers': papers_str,
    }
    messages = openai_format_prompt_construct(prompt_template, template_input)

    return model_prompting(
        model_name,
        messages,
        return_num,
        max_token_num,
        temperature,
        top_p,
        stream,
    )


@beartype
def brainstorm_idea_prompting(
    insights: List[Dict[str, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    insights_str = map_insight_list_to_str(insights)
    template_input = {'insights': insights_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
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
    template_input = {'ideas': ideas_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
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
) -> List[str]:
    idea_str = map_idea_to_str(idea)
    papers_str = map_paper_list_to_str(papers)
    template_input = {'idea': idea_str, 'papers': papers_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
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
def write_review_prompting(
    paper: Dict[str, str],
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
    paper_str = map_paper_to_str(paper)
    summary_template_input = {'paper': paper_str}
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

    strength_template_input = {'paper': paper_str, 'summary': summary}
    strength_messages = openai_format_prompt_construct(
        strength_prompt_template, strength_template_input
    )
    weakness_template_input = {'paper': paper_str, 'summary': summary}
    weakness_messages = openai_format_prompt_construct(
        weakness_prompt_template, weakness_template_input
    )
    ethical_template_input = {'paper': paper_str, 'summary': summary}
    ethical_messages = openai_format_prompt_construct(
        ethical_prompt_template, ethical_template_input
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
        'paper': paper_str,
        'summary': summary,
        'strength': strength,
        'weakness': weakness,
        'ethical_concerns': ethical_concerns,
    }
    score_messages = openai_format_prompt_construct(
        score_prompt_template, score_template_input
    )
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
    paper: Dict[str, str],
    reviews: List[Dict[str, Union[int, str]]],
    rebuttals: List[Dict[str, str]],
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
    paper_str = map_paper_to_str(paper)
    reviews_str = map_review_list_to_str(reviews)
    rebuttals_str = map_rebuttal_list_to_str(rebuttals)
    summary_template_input = {
        'paper': paper_str,
        'reviews': reviews_str,
        'rebuttals': rebuttals_str,
    }
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

    strength_template_input = {
        'paper': paper_str,
        'reviews': reviews_str,
        'rebuttals': rebuttals_str,
        'summary': summary,
    }
    weakness_template_input = {
        'paper': paper_str,
        'reviews': reviews_str,
        'rebuttals': rebuttals_str,
        'summary': summary,
    }
    ethical_template_input = {
        'paper': paper_str,
        'reviews': reviews_str,
        'rebuttals': rebuttals_str,
        'summary': summary,
    }
    strength_messages = openai_format_prompt_construct(
        strength_prompt_template, strength_template_input
    )
    weakness_messages = openai_format_prompt_construct(
        weakness_prompt_template, weakness_template_input
    )
    ethical_messages = openai_format_prompt_construct(
        ethical_prompt_template, ethical_template_input
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
        'paper': paper_str,
        'reviews': reviews_str,
        'rebuttals': rebuttals_str,
        'summary': summary,
        'strength': strength,
        'weakness': weakness,
        'ethical_concerns': ethical_concerns,
    }
    decision_messages = openai_format_prompt_construct(
        decision_prompt_template, decision_template_input
    )
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
    paper: Dict[str, str],
    review: Dict[str, Union[int, str]],
    model_name: str,
    prompt_template: Dict[str, Union[str, List[str]]],
    return_num: Optional[int] = 1,
    max_token_num: Optional[int] = 512,
    temperature: Optional[float] = 0.0,
    top_p: Optional[float] = None,
    stream: Optional[bool] = None,
) -> List[str]:
    paper_str = map_paper_to_str(paper)
    review_str = map_review_to_str(review)
    template_input = {'paper': paper_str, 'review': review_str}
    messages = openai_format_prompt_construct(prompt_template, template_input)
    return model_prompting(
        model_name,
        messages,
        return_num=return_num,
        max_token_num=max_token_num,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
    )
