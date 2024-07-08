from beartype import beartype
from beartype.typing import Dict, List, Tuple, Union

from .model_prompting import model_prompting
from .paper_collector import get_related_papers
from .string_mapper import (
    map_idea_list_to_str,
    map_idea_to_str,
    map_insights_to_str,
    map_message_to_str,
    map_paper_list_to_str,
    map_paper_to_str,
    map_rebuttal_list_to_str,
    map_review_list_to_str,
    map_review_to_str,
)

# =======================================


@beartype
def summarize_research_direction_prompting(
    personal_info: str,
    prompt_template: str,
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
) -> List[str]:
    """
    Summarize research direction based on personal research history
    """
    template_input = {'personal_info': personal_info}
    prompt = prompt_template.format_map(template_input)
    return model_prompting(model_name, prompt)


@beartype
def find_collaborators_prompting(
    input: Dict[str, str],
    self_profile: Dict[str, str],
    collaborator_profiles: Dict[str, str],
    parameter: float = 0.5,
    max_number: int = 3,
    model_name: str = 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
) -> List[str]:
    self_serialize = [
        f'Name: {name}\nProfile: {self_profile[name]}'
        for _, name in enumerate(self_profile.keys())
    ]
    self_serialize_all = '\n\n'.join(self_serialize)

    task_serialize = [
        f'Time: {timestamp}\nAbstract: {input[timestamp]}\n'
        for _, timestamp in enumerate(input.keys())
    ]
    task_serialize_all = '\n\n'.join(task_serialize)

    collaborator_serialize = [
        f'Name: {name}\nProfile: {collaborator_profiles[name]}'
        for _, name in enumerate(collaborator_profiles.keys())
    ]
    collaborator_serialize_all = '\n\n'.join(collaborator_serialize)

    prompt_template = (
        'Given the name and profile of me, could you find {max_number} collaborators for the following collaboration task?'
        'Here is my profile: {self_serialize_all}'
        'The collaboration task include: {task_serialize_all}'
        'Here are a full list of the names and profiles of potential collaborators: {collaborators_serialize_all}'
        "Generate the collaborator in a list separated by '-' for each collaborator"
    )
    input = {
        'max_number': str(max_number),
        'self_serialize_all': self_serialize_all,
        'task_serialize_all': task_serialize_all,
        'collaborators_serialize_all': collaborator_serialize_all,
    }
    prompt = prompt_template.format_map(input)
    return model_prompting(model_name, prompt)


# =======================================


@beartype
def review_literature_prompting(
    profile: Dict[str, str],
    papers: List[Dict[str, str]],
    domains: List[str],
    model_name: str,
    prompt_template_query_paper: str,
    prompt_template_review_literature: str,
) -> List[str]:
    query_paper_prompt = prompt_template_query_paper.format_map(
        {'profile_bio': profile['bio'], 'domains': '; '.join(domains)}
    )

    corpus = [paper['abstract'] for paper in papers]
    related_papers = get_related_papers(corpus, query_paper_prompt, num=1)

    review_literature_prompt = prompt_template_review_literature.format_map(
        {
            'profile_bio': profile['bio'],
            'domains': '; '.join(domains),
            'papers': '; '.join(related_papers),
        }
    )
    return model_prompting(model_name, review_literature_prompt)


@beartype
def brainstorm_idea_prompting(
    insights: List[Dict[str, str]],
    model_name: str,
    prompt_template: str,
) -> List[str]:
    insights_str = map_insights_to_str(insights)
    prompt = prompt_template.format_map({'insights': insights_str})
    return model_prompting(model_name, prompt)


@beartype
def discuss_idea_prompting(
    ideas: List[Dict[str, str]],
    model_name: str,
    prompt_template: str,
) -> List[str]:
    ideas_str = map_idea_list_to_str(ideas)
    prompt = prompt_template.format_map({'ideas': ideas_str})
    return model_prompting(model_name, prompt)


@beartype
def write_paper_prompting(
    idea: Dict[str, str],
    papers: List[Dict[str, str]],
    model_name: str,
    prompt_template: str,
) -> List[str]:
    idea_str = map_idea_to_str(idea)
    papers_str = map_paper_list_to_str(papers)
    prompt = prompt_template.format_map({'idea': idea_str, 'papers': papers_str})
    return model_prompting(model_name, prompt)


@beartype
def write_review_prompting(
    paper: Dict[str, str],
    model_name: str,
    summary_prompt_template: str,
    strength_prompt_template: str,
    weakness_prompt_template: str,
    score_prompt_template: str,
) -> Tuple[str, str, str, int]:
    paper_str = map_paper_to_str(paper)
    summary_prompt = summary_prompt_template.format_map({'paper': paper_str})
    summary = model_prompting(model_name, summary_prompt)[0]

    strength_prompt = strength_prompt_template.format_map(
        {'paper': paper_str, 'summary': summary}
    )
    weakness_prompt = weakness_prompt_template.format_map(
        {'paper': paper_str, 'summary': summary}
    )
    strength = model_prompting(model_name, strength_prompt)[0]
    weakness = model_prompting(model_name, weakness_prompt)[0]

    score_prompt = score_prompt_template.format_map(
        {
            'paper': paper_str,
            'summary': summary,
            'strength': strength,
            'weakness': weakness,
        }
    )
    score_str = model_prompting(model_name, score_prompt)[0]
    score = int(score_str[0]) if score_str[0].isdigit() else 0

    return summary, strength, weakness, score


@beartype
def write_meta_review_prompting(
    paper: Dict[str, str],
    reviews: List[Dict[str, Union[int, str]]],
    rebuttals: List[Dict[str, str]],
    model_name: str,
    summary_prompt_template: str,
    strength_prompt_template: str,
    weakness_prompt_template: str,
    decision_prompt_template: str,
) -> Tuple[str, str, str, bool]:
    paper_str = map_paper_to_str(paper)
    reviews_str = map_review_list_to_str(reviews)
    rebuttals_str = map_rebuttal_list_to_str(rebuttals)
    summary_prompt = summary_prompt_template.format_map(
        {'paper': paper_str, 'reviews': reviews_str, 'rebuttals': rebuttals_str}
    )
    summary = model_prompting(model_name, summary_prompt)[0]

    strength_prompt = strength_prompt_template.format_map(
        {
            'paper': paper_str,
            'reviews': reviews_str,
            'rebuttals': rebuttals_str,
            'summary': summary,
        }
    )
    weakness_prompt = weakness_prompt_template.format_map(
        {
            'paper': paper_str,
            'reviews': reviews_str,
            'rebuttals': rebuttals_str,
            'summary': summary,
        }
    )
    strength = model_prompting(model_name, strength_prompt)[0]
    weakness = model_prompting(model_name, weakness_prompt)[0]

    decision_prompt = decision_prompt_template.format_map(
        {
            'paper': paper_str,
            'reviews': reviews_str,
            'rebuttals': rebuttals_str,
            'summary': summary,
            'strength': strength,
            'weakness': weakness,
        }
    )
    decision_str = model_prompting(model_name, decision_prompt)
    decision = 'accept' in decision_str[0].lower()

    return summary, strength, weakness, decision


@beartype
def write_rebuttal_prompting(
    paper: Dict[str, str],
    review: Dict[str, Union[int, str]],
    model_name: str,
    prompt_template: str,
) -> List[str]:
    paper_str = map_paper_to_str(paper)
    review_str = map_review_to_str(review)
    prompt = prompt_template.format_map({'paper': paper_str, 'review': review_str})
    return model_prompting(model_name, prompt)


@beartype
def discuss_prompting(
    message: Dict[str, str],
    model_name: str,
    prompt_template: str,
) -> List[str]:
    message_str = map_message_to_str(message)
    prompt = prompt_template.format_map({'message': message_str})
    return model_prompting(model_name, prompt)
