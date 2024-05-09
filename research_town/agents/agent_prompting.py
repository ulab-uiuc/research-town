import time
from typing import Any, Dict, List, Tuple

import openai

from ..utils.paper_collection import (
    get_bert_embedding,
    neiborhood_search,
)

KEY = "7a1821d4e4a3e41e3d523e97e0fd8950dedac2824aef99cb19d550500cb21a42"
openai.api_base = "https://api.together.xyz"
llm_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"


def summarize_research_field(
    profile: Dict[str, str],
    keywords: List[str],
    dataset: Dict[str, Any],
    data_embedding: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
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
    title_chunk = []
    data_embedding_l = []
    for k in dataset.keys():
        title_chunk.extend(dataset[k]["info"])
        text_chunk_l.extend(dataset[k]["abstract"])
        data_embedding_l.extend(data_embedding[k])

    chunks_embedding_text_all = data_embedding_l
    num_chunk = 10

    neib_all = neiborhood_search(chunks_embedding_text_all, query_embedding, num_chunk)
    neib_all = neib_all.reshape(-1)

    context = []
    retrieve_paper = []
    for i in neib_all:
        context.append(text_chunk_l[i])
        retrieve_paper.append(title_chunk[i])

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
    return content_l, retrieve_paper


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