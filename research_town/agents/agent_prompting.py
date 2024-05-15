import time
from typing import Any, Dict, List

import openai

from ..utils.paper_collection import (
    get_bert_embedding,
    neiborhood_search,
)

KEY = "8296dfb726872f46701fdd87468fc1d8af83965efb49963ee876194e316b041a"
openai.api_base = "https://api.together.xyz"
llm_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"


def summarize_research_field(
    profile: Dict[str, str],
    keywords: List[str],
    dataset: Dict[str, Any],
    data_embedding: Dict[str, Any],
) -> List[str]:
    openai.api_key = KEY
    query_format = (
        "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgrounds and trends in this field (related to my profile if possible)."
        "Here is my profile: {profile}"
        "Here are the keywords: {keywords}"
    )

    input = {"profile": profile, "keywords": keywords}

    query = query_format.format_map(input)

    query_embedding = get_bert_embedding([query])
    text_chunk_l = []
    data_embedding_l = []
    for k in dataset.keys():
        text_chunk_l.extend(dataset[k]["abstract"])
        data_embedding_l.extend(data_embedding[k])

    chunks_embedding_text_all = data_embedding_l
    num_chunk = 10

    neib_all = neiborhood_search(
        chunks_embedding_text_all, query_embedding, num_chunk)
    neib_all = neib_all.reshape(-1)

    context = []
    for i in neib_all:
        context.append(text_chunk_l[i])

    input["papers"] = "; ".join(context)
    prompt = query_format.format_map(input)

    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
    except Exception:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )

    content = completion.choices[0].message["content"]
    content_l = [content]
    return content_l


def generate_ideas(trend: str) -> List[str]:
    prompt_qa = (
        "Here is a high-level summarized trend of a research field {trend}. "
        "How do you view this field? Do you have any novel ideas or insights? "
        "Please give me 3 to 5 novel ideas and insights in bullet points. Each bullet point should be concise, containing 2 or 3 sentences."
    )
    openai.api_key = KEY
    input = {"trend": trend}
    prompt = prompt_qa.format_map(input)
    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=1,
        )
    except Exception:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=1,
        )
    content = completion.choices[0].message["content"]
    return [content]


def summarize_research_direction(personal_info: str) -> List[str]:
    prompt_qa = (
        "Based on the list of the researcher's first person persona from different times, please write a comprehensive first person persona. "
        "Focus more on more recent personas. Be concise and clear (around 300 words). "
        "Here are the personas from different times: {personalinfo}"
    )
    openai.api_key = KEY
    input = {"personalinfo": personal_info}
    prompt = prompt_qa.format_map(input)
    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    except Exception:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    content = completion.choices[0].message["content"]
    return [content]


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

    prompt_qa = (
        "Please write a paper based on the following ideas and external data. To save time, you only need to write the abstract. "
        "You might use two or more of these ideas if they are related and works well together. "
        "Here are the ideas: {ideas_serialize_all}"
        "Here are the external data, which is a list abstracts of related papers: {papers_serialize_all}"
    )

    openai.api_key = KEY
    input = {"ideas_serialize_all": ideas_serialize_all,
             "papers_serialize_all": papers_serialize_all}

    prompt = prompt_qa.format_map(input)
    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    except Exception:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    content = completion.choices[0].message["content"]
    return [content]


def review_paper_(titles: Dict[str, str], external_data: Dict[str, str]):
    """
    Review paper from using list, and external data (published papers)
    """

    titles_serialize = []
    for _, timestamp in enumerate(titles.keys()):
        title_entry = f"Time: {timestamp}\nPaper: {external_data[timestamp]}"
        titles_serialize.append(title_entry)
    titles_serialize_all = "\n\n".join(titles_serialize)

    papers_serialize = []
    for _, timestamp in enumerate(external_data.keys()):
        paper_entry = f"Time: {timestamp}\nPaper: {external_data[timestamp]}"
        papers_serialize.append(paper_entry)
    papers_serialize_all = "\n\n".join(papers_serialize)

    prompt_qa = (
        "Please give some reviews based on the following inputs and external data."
        "You might use two or more of these titles if they are related and works well together."
        "Here are the titles: {titles_serialize_all}"
        "Here are the external data, which is a list of related papers: {papers_serialize_all}"
    )

    openai.api_key = KEY
    input = {"titles_serialize_all": titles_serialize_all,
             "papers_serialize_all": papers_serialize_all}

    prompt = prompt_qa.format_map(input)
    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    except Exception:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    content = completion.choices[0].message["content"]
    return [content]


def communicate_with_multiple_researchers(input: Dict[str, str]):
    """
    This is a single-round chat method. One that contains a chat history can better enable
    """
    single_round_chat_serialize = [
        f"Message from researcher named {name}: {message}" for name, message in input.items()]
    single_round_chat_serialize_all = "\n".join(single_round_chat_serialize)
    prompt_qa = (
        "Please continue in a conversation with other fellow researchers for me, where you will address their concerns in a scholarly way. "
        "Here are the messages from other researchers: {single_round_chat_serialize_all}"
    )
    openai.api_key = KEY
    input = {"single_round_chat_serialize_all": single_round_chat_serialize_all}
    prompt = prompt_qa.format_map(input)
    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    except Exception:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            seed=42,
            top_p=0,
        )
    content = completion.choices[0].message["content"]
    return [content]
