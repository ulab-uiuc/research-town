from typing import Dict, List, Tuple

from .model_prompting import model_prompting
from .paper_collector import get_related_papers


def summarize_research_field_prompting(
    profile: Dict[str, str],
    keywords: List[str],
    papers: Dict[str, Dict[str, List[str]]],
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    """
    Summarize research field based on profile, keywords, written papers
    """
    query_template = (
        "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and trends in this field (related to my profile if possible)."
        "Here is my profile: {profile}"
        "Here are the keywords: {keywords}"
    )
    template_input = {
        "profile": profile,
        "keywords": "; ".join(keywords)
    }
    query = query_template.format_map(template_input)

    corpus = [abstract for papers in papers.values()
              for abstract in papers["abstract"]]

    related_papers = get_related_papers(corpus, query, num=1)

    template_input = {
        "profile": profile,
        "keywords": keywords,
        "papers": "; ".join(related_papers)
    }
    prompt_template = (
        "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and trends in this field (related to my profile if possible)."
        "Here is my profile: {profile}"
        "Here are the keywords: {keywords}"
        "Here are some recent paper titles and abstracts: {papers}"
    )
    prompt = prompt_template.format_map(template_input)

    return model_prompting(model_name, prompt)


def find_collaborators_prompting(
    input: Dict[str, str],
    self_profile: Dict[str, str],
    collaborator_profiles: Dict[str, str],
    parameter: float = 0.5,
    max_number: int = 3,
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    self_serialize = [
        f"Name: {name}\nProfile: {self_profile[name]}" for _, name in enumerate(self_profile.keys())]
    self_serialize_all = "\n\n".join(self_serialize)

    task_serialize = [f"Time: {timestamp}\nAbstract: {input[timestamp]}\n" for _,
                      timestamp in enumerate(input.keys())]
    task_serialize_all = "\n\n".join(task_serialize)

    collaborator_serialize = [
        f"Name: {name}\nProfile: {collaborator_profiles[name]}" for _, name in enumerate(collaborator_profiles.keys())]
    collaborator_serialize_all = "\n\n".join(collaborator_serialize)

    prompt_qa = (
        "Given the name and profile of me, could you find {max_number} collaborators for the following collaboration task?"
        "Here is my profile: {self_serialize_all}"
        "The collaboration task include: {task_serialize_all}"
        "Here are a full list of the names and profiles of potential collaborators: {collaborators_serialize_all}"
        "Generate the collaborator in a list separated by '-' for each collaborator"
    )
    input = {"max_number": str(max_number), "self_serialize_all": self_serialize_all,
             "task_serialize_all": task_serialize_all, "collaborators_serialize_all": collaborator_serialize_all}
    prompt = prompt_qa.format_map(input)
    return model_prompting(model_name, prompt)


def generate_ideas_prompting(
    trend: str,
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    """
    Generate research ideas based on the trending of one research field
    """
    prompt_template = (
        "Here is a high-level summarized trend of a research field {trend}. "
        "How do you view this field? Do you have any novel ideas or insights? "
        "Please give me 3 to 5 novel ideas and insights in bullet points. Each bullet point should be concise, containing 2 or 3 sentences."
    )
    template_input = {"trend": trend}
    prompt = prompt_template.format_map(template_input)
    return model_prompting(model_name, prompt)


def summarize_research_direction_prompting(
    personal_info: str,
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    """
    Summarize research direction based on personal research history
    """
    prompt_template = (
        "Based on the list of the researcher's first person persona from different times, please write a comprehensive first person persona. "
        "Focus more on more recent personas. Be concise and clear (around 300 words). "
        "Here are the personas from different times: {personalinfo}"
    )
    template_input = {"personalinfo": personal_info}
    prompt = prompt_template.format_map(template_input)
    return model_prompting(model_name, prompt)


def write_paper_abstract_prompting(
    ideas: List[str],
    papers: Dict[str, Dict[str, List[str]]],
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    """
    Write paper using ideas from list, and external data (published papers)
    """
    ideas_serialize = [f"{i}: {idea}" for i, idea in enumerate(ideas)]
    ideas_serialize_all = "\n".join(ideas_serialize)

    papers_serialize = []

    for i, timestamp in enumerate(papers.keys()):
        abstracts = papers[timestamp]['abstract']
        formatted_abstracts = '\nAbstract: '.join(abstracts)
        paper_entry = f"Time: {timestamp}\nAbstract: {formatted_abstracts}\n"
        papers_serialize.append(paper_entry)

    papers_serialize_all = "\n\n".join(papers_serialize)

    prompt_template = (
        "Please write a paper based on the following ideas and external data. To save time, you only need to write the abstract. "
        "You might use two or more of these ideas if they are related and works well together. "
        "Here are the ideas: {ideas_serialize_all}"
        "Here are the external data, which is a list abstracts of related papers: {papers_serialize_all}"
    )

    template_input = {"ideas_serialize_all": ideas_serialize_all,
                      "papers_serialize_all": papers_serialize_all}
    prompt = prompt_template.format_map(template_input)
    return model_prompting(model_name, prompt)


def review_score_prompting(paper_review: str, model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1") -> int:
    prompt_qa = (
        "Please provide a score for the following reviews. The score should be between 1 and 10, where 1 is the lowest and 10 is the highest. Only returns one number score."
        "Here are the reviews: {paper_review}"
    )
    input = {"paper_review": paper_review}
    prompt = prompt_qa.format_map(input)
    score_str = model_prompting(model_name, prompt)
    if score_str[0].isdigit():
        return int(score_str[0])
    else:
        return 0


def review_paper_prompting(paper: Dict[str, str],  model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",) -> List[str]:
    """
    Review paper from using list, and external data (published papers)
    """

    papers_serialize = []
    for _, title in enumerate(paper.keys()):
        paper_entry = f"Title: {title}\nPaper: {paper[title]}"
        papers_serialize.append(paper_entry)
    papers_serialize_all = "\n\n".join(papers_serialize)

    prompt_qa = (
        "Please give some reviews based on the following inputs and external data."
        "You might use two or more of these titles if they are related and works well together."
        "Here are the external data, which is a list of related papers: {papers_serialize_all}"
    )

    input = {"papers_serialize_all": papers_serialize_all}

    prompt = prompt_qa.format_map(input)
    return model_prompting(model_name, prompt)


def make_review_decision_prompting(
    paper: Dict[str, str], 
    review: Dict[str, Tuple[int, str]], 
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    paper_serialize = []
    for _, title in enumerate(paper.keys()):
        abstract = paper[title]
        paper_entry = f"Title: {title}\nAbstract:{abstract}\n"
        paper_serialize.append(paper_entry)
    paper_serialize_all = "\n\n".join(paper_serialize)

    review_serialize = []
    for _, name in enumerate(review.keys()):
        content = review[name]
        review_entry = f"Name: {name}\nContent: {content}\n"
        review_serialize.append(review_entry)
    review_serialize_all = "\n\n".join(review_serialize)

    prompt_template = (
        "Please make an review decision to decide whether the following submission should be accepted or rejected by an academic conference. Here are several reviews from reviewers for this submission. Please indicate your review decision as accept or reject."
        "Here is the submission: {paper_serialize_all}"
        "Here are the reviews: {review_serialize_all}"
    )
    template_input = {"paper_serialize_all": paper_serialize_all,
                      "review_serialize_all": review_serialize_all}
    prompt = prompt_template.format_map(template_input)
    return model_prompting(model_name, prompt)


def rebut_review_prompting(
    paper: Dict[str, str], 
    review: Dict[str, Tuple[int, str]], 
    decision: Dict[str, Tuple[bool, str]], 
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    submission_serialize = []
    for _, title in enumerate(paper.keys()):
        abstract = paper[title]
        submission_entry = f"Title: {title}\nAbstract:{abstract}\n"
        submission_serialize.append(submission_entry)
    submission_serialize_all = "\n\n".join(submission_serialize)

    review_serialize = []
    for _, name in enumerate(review.keys()):
        content = review[name]
        review_entry = f"Name: {name}\nContent: {content}\n"
        review_serialize.append(review_entry)
    review_serialize_all = "\n\n".join(review_serialize)

    decision_serialize = []
    for _, name in enumerate(decision.keys()):
        content = decision[name]
        decision_entry = f"Name: {name}\nDecision: {content}\n"
        decision_serialize.append(decision_entry)
    decision_serialize_all = "\n\n".join(decision_serialize)

    prompt_template = (
        "Please write a rebuttal for the following submission you have made to an academic conference. Here are the reviews and decisions from the reviewers. Your rebuttal should rebut the reviews to convince the reviewers to accept your submission."
        "Here is the submission: {submission_serialize_all}"
        "Here are the reviews: {review_serialize_all}"
        "Here are the decisions: {decision_serialize_all}"
    )
    template_input = {"submission_serialize_all": submission_serialize_all,
                      "review_serialize_all": review_serialize_all, "decision_serialize_all": decision_serialize_all}
    prompt = prompt_template.format_map(template_input)
    return model_prompting(model_name, prompt)


def communicate_with_multiple_researchers_prompting(
    messages: Dict[str, str],
    model_name: str = "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
) -> List[str]:
    """
    This is a single-round chat method. One that contains a chat history can better enable
    """
    single_round_chat_serialize = [
        f"Message from researcher named {name}: {message}" for name, message in messages.items()]
    single_round_chat_serialize_all = "\n".join(single_round_chat_serialize)
    prompt_template = (
        "Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. "
        "Here are the messages from other researchers: {single_round_chat_serialize_all}"
    )
    template_input = {
        "single_round_chat_serialize_all": single_round_chat_serialize_all}
    prompt = prompt_template.format_map(template_input)
    return model_prompting(model_name, prompt)
