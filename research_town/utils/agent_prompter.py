from beartype import beartype
from beartype.typing import Dict, List, Union

from .model_prompting import model_prompting
from .paper_collector import get_related_papers
from .string_mapper import (
    map_idea_list_to_str,
    map_message_to_str,
    map_paper_list_to_str,
    map_paper_to_str,
    map_review_list_to_str,
    map_review_to_str,
)

# =======================================


@beartype
def summarize_research_direction_prompting(
    personal_info: str,
    model_name: str,
) -> List[str]:
    """
    Summarize research direction based on personal research history
    """
    prompt_template = (
        "Based on the list of the researcher's first person persona from different times, please write a comprehensive first person persona. "
        'Focus more on more recent personas. Be concise and clear (around 300 words). '
        'Here are the personas from different times: {personalinfo}'
    )
    template_input = {'personalinfo': personal_info}
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
def read_paper_prompting(
    profile: Dict[str, str],
    papers: List[Dict[str, str]],
    domains: List[str],
    model_name: str,
) -> List[str]:
    query_template = (
        'Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and insights in this field (related to my profile if possible).'
        'Here is my profile biology: {profile_bio}'
        'Here are the domains: {domains}'
    )
    prompt_template = (
        'Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and insights in this field (related to my profile if possible).'
        'Here is my profile biology: {profile_bio}'
        'Here are the research domains: {domains}'
        'Here are some recent paper titles and abstracts: {papers}'
    )

    query = query_template.format_map(
        {'profile_bio': profile['bio'], 'domains': '; '.join(domains)}
    )

    corpus = [paper['abstract'] for paper in papers]
    related_papers = get_related_papers(corpus, query, num=1)

    prompt = prompt_template.format_map(
        {
            'profile_bio': profile['bio'],
            'domains': '; '.join(domains),
            'papers': '; '.join(related_papers),
        }
    )
    return model_prompting(model_name, prompt)


@beartype
def think_idea_prompting(
    insight: Dict[str, str],
    model_name: str,
) -> List[str]:
    prompt_template = (
        'Here is a high-level summarized insight of a research field {insight}. '
        'How do you view this field? Do you have any novel ideas or insights? '
        'Please give me 3 to 5 novel ideas and insights in bullet points. Each bullet point should be concise, containing 2 or 3 sentences.'
    )
    prompt = prompt_template.format_map({'insight': insight['content']})
    return model_prompting(model_name, prompt)


@beartype
def write_paper_prompting(
    ideas: List[Dict[str, str]],
    papers: List[Dict[str, str]],
    model_name: str,
) -> List[str]:
    ideas_str = map_idea_list_to_str(ideas)
    papers_str = map_paper_list_to_str(papers)

    prompt_template = (
        'Please write a paper based on the following ideas and external data. To save time, you only need to write the abstract. '
        'You might use two or more of these ideas if they are related and works well together. '
        'Here are the ideas: {ideas}'
        'Here are the external data, which is a list abstracts of related papers: {papers}'
    )

    prompt = prompt_template.format_map({'ideas': ideas_str, 'papers': papers_str})
    return model_prompting(model_name, prompt)


@beartype
def review_score_prompting(paper_review: str, model_name: str) -> int:
    prompt_template = (
        'Please provide a score for the following reviews. The score should be between 1 and 10, where 1 is the lowest and 10 is the highest. Only returns one number score.'
        'Here are the reviews: {paper_review}'
    )
    prompt = prompt_template.format_map(
        {
            'paper_review': paper_review,
        }
    )
    score_str = model_prompting(model_name, prompt)[0]
    return int(score_str[0]) if score_str[0].isdigit() else 0


@beartype
def review_paper_prompting(
    paper: Dict[str, str],
    model_name: str,
) -> List[str]:
    papers_str = map_paper_to_str(paper)
    prompt_template = (
        'Please give some reviews based on the following inputs and external data.'
        'You might use two or more of these titles if they are related and works well together.'
        'Here are the external data, which is a list of related papers: {papers}'
    )

    prompt = prompt_template.format_map({'papers': papers_str})
    return model_prompting(model_name, prompt)


@beartype
def write_meta_review_prompting(
    paper: Dict[str, str],
    reviews: List[Dict[str, Union[int, str]]],
    model_name: str,
) -> List[str]:
    paper_str = map_paper_to_str(paper)
    reviews_str = map_review_list_to_str(reviews)

    prompt_template = (
        'Please make an review decision to decide whether the following submission should be accepted or rejected by an academic conference. Here are several reviews from reviewers for this submission. Please indicate your review decision as accept or reject.'
        'Here is the submission: {paper}'
        'Here are the reviews: {reviews}'
    )
    prompt = prompt_template.format_map({'paper': paper_str, 'reviews': reviews_str})
    return model_prompting(model_name, prompt)


@beartype
def write_rebuttal_prompting(
    paper: Dict[str, str],
    review: Dict[str, Union[int, str]],
    model_name: str,
) -> List[str]:
    paper_str = map_paper_to_str(paper)
    review_str = map_review_to_str(review)

    prompt_template = (
        'Please write a rebuttal for the following submission you have made to an academic conference. Here are the reviews and decisions from the reviewers. Your rebuttal should rebut the reviews to convince the reviewers to accept your submission.'
        'Here is the submission: {paper}'
        'Here are the reviews: {review}'
    )
    prompt = prompt_template.format_map({'paper': paper_str, 'review': review_str})
    return model_prompting(model_name, prompt)


@beartype
def discuss_prompting(
    message: Dict[str, str],
    model_name: str,
) -> List[str]:
    message_str = map_message_to_str(message)
    prompt_template = (
        'Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. '
        'Here are the messages from other researchers: {message}'
    )
    prompt = prompt_template.format_map({'message': message_str})
    return model_prompting(model_name, prompt)
