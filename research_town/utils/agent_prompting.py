from typing import Any, Dict, List, Optional

import openai

from .decorator import exponential_backoff
from .paper_collection import get_bert_embedding, neiborhood_search

KEY = "TOGETHER_API_KEY"
openai.api_base = "https://api.together.xyz"
openai.api_key = KEY
llm_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"


@exponential_backoff(retries=5, base_wait_time=1)
def openai_prompting(
    llm_model: str,
    prompt: str,
    return_num: Optional[int] = 2,
    max_token_num: Optional[int] = 512,
) -> List[str]:
    completion = openai.Completion.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_token_num,
        num=return_num,
    )
    content = completion.choices[0].message["content"]
    content_l = [content]
    return content_l


def get_query_embedding(query: str) -> Any:
    return get_bert_embedding([query])


def find_nearest_neighbors(data_embeddings: List[Any], query_embedding: Any, num_neighbors: int) -> List[int]:
    neighbors = neiborhood_search(data_embeddings, query_embedding, num_neighbors)
    return neighbors.reshape(-1).tolist()


def summarize_research_field(
    profile: Dict[str, str],
    keywords: List[str],
    dataset: Dict[str, Any],
    data_embedding: Dict[str, Any],
) -> List[str]:
    """
    Summarize research field based on profile, keywords, written papers
    """
    query_template = (
        "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and trends in this field (related to my profile if possible)."
        "Here is my profile: {profile}"
        "Here are the keywords: {keywords}"
    )

    template_input = {"profile": profile, "keywords": keywords}
    query = query_template.format_map(template_input)

    query_embedding = get_query_embedding(query)

    text_chunks = [abstract for papers in dataset.values() for abstract in papers["abstract"]]
    data_embeddings = [embedding for embeddings in data_embedding.values() for embedding in embeddings]

    nearest_indices = find_nearest_neighbors(data_embeddings, query_embedding, num_neighbors=10)
    context = [text_chunks[i] for i in nearest_indices]

    template_input["papers"] = "; ".join(context)
    prompt = query_template.format_map(template_input)

    return openai_prompting(llm_model, prompt)


def generate_ideas(trend: str) -> List[str]:
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
    return openai_prompting(llm_model, prompt)


def summarize_research_direction(personal_info: str) -> List[str]:
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
    return openai_prompting(llm_model, prompt)


def write_paper_abstract(ideas: List[str], external_data: Dict[str, Dict[str, List[str]]]):
    """
    Write paper using ideas from list, and external data (published papers)
    """
    ideas_serialize = [f"{i}: {idea}" for i, idea in enumerate(ideas)]
    ideas_serialize_all = "\n".join(ideas_serialize)

    papers_serialize = []

    for i, timestamp in enumerate(external_data.keys()):
        abstracts = external_data[timestamp]['abstract']
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

    template_input = {"ideas_serialize_all": ideas_serialize_all, "papers_serialize_all": papers_serialize_all}
    prompt = prompt_template.format_map(template_input)
    return openai_prompting(llm_model, prompt)


def communicate_with_multiple_researchers(input: Dict[str, str]):
    """
    This is a single-round chat method. One that contains a chat history can better enable
    """
    single_round_chat_serialize = [f"Message from researcher named {name}: {message}" for name, message in input.items()]
    single_round_chat_serialize_all = "\n".join(single_round_chat_serialize)
    prompt_template = (
        "Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. "
        "Here are the messages from other researchers: {single_round_chat_serialize_all}"
    )
    template_input = {"single_round_chat_serialize_all": single_round_chat_serialize_all}
    prompt = prompt_template.format_map(template_input)
    return openai_prompting(llm_model, prompt)
