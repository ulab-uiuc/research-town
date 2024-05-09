import datetime
import json
import os
import time
from typing import Any, Dict, List, Tuple

import arxiv
import faiss
import openai
import torch
from arxiv import Client, Search
from tqdm import tqdm
from transformers import BertModel, BertTokenizer

KEY = "TOGETHER_API_KEY"
openai.api_base = "https://api.together.xyz"
llm_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"


def show_time():
    time_stamp = (
        "\033[1;31;40m["
        + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        + "]\033[0m"
    )

    return time_stamp


def text_wrap(text):
    return "\033[1;31;40m" + str(text) + "\033[0m"


def write_to_json(data, output_file):
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def count_entries_in_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        return len(data)


def clean_title(title):
    cleaned_title = title.replace("\n", " ").strip()
    cleaned_title = os.path.splitext(cleaned_title)[0]
    cleaned_title = (
        cleaned_title.replace(":", "")
        .replace("- ", " ")
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )

    return cleaned_title


def get_bert_embedding(instructions: List[str]) -> List[torch.Tensor]:
    tokenizer = BertTokenizer.from_pretrained("facebook/contriever")
    model = BertModel.from_pretrained("facebook/contriever").to(torch.device("cpu"))


    encoded_input_all = [
        tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(
            torch.device("cpu")
        )
        for text in instructions
    ]

    with torch.no_grad():
        emb_list = []
        for inter in encoded_input_all:
            emb = model(**inter)
            emb_list.append(emb["last_hidden_state"].mean(1))
    return emb_list


def neiborhood_search(
    corpus_data: List[torch.Tensor], query_data: List[torch.Tensor], num: int
) -> torch.Tensor:
    d = 768
    neiborhood_num = num
    xq = torch.cat(query_data, 0).cpu().numpy()
    xb = torch.cat(corpus_data, 0).cpu().numpy()
    index = faiss.IndexFlatIP(d)
    xq = xq.astype("float32")
    xb = xb.astype("float32")
    faiss.normalize_L2(xq)
    faiss.normalize_L2(xb)
    index.add(xb)  # add vectors to the index
    data, index = index.search(xq, neiborhood_num)

    return index


#######
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


def get_authors(authors: List[str], first_author: bool = False) -> str:
    if first_author:
        return authors[0]
    return ", ".join(authors)


def get_daily_papers(
    topic: str, query: str = "slam", max_results: int = 2
) -> Tuple[Dict[str, Dict[str, List[str]]], str]:
    search_engine = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    content: Dict[str, Dict[str, List[str]]] = {}
    newest_day = ""
    for result in search_engine.results():
        paper_title = result.title
        paper_url = result.entry_id
        paper_abstract = result.summary.replace("\n", " ")
        publish_time = result.published.date()
        newest_day = publish_time
        if publish_time in content:
            content[publish_time]['abstract'].append(paper_title + ": " + paper_abstract)
            content[publish_time]['info'].append(paper_title + ": " + paper_url)
        else:
            content[publish_time] = {}
            content[publish_time]['abstract'] = [paper_title + ": " + paper_abstract]
            content[publish_time]['info'] = [paper_title + ": " + paper_url]
    return content, newest_day


def author_position(author, author_list):
    for ind, i in enumerate(author_list):
        if author.lower() == i.lower():
            return ind + 1

    return "NULL"


def co_author_frequency(
    author: str, author_list: List[str], co_authors: Dict[str, int]
) -> Dict[str, int]:
    for ind, i in enumerate(author_list):
        if author.lower() == i.lower():
            continue
        if i in co_authors:
            co_authors[i] += 1
        else:
            co_authors[i] = 1
    return co_authors


def co_author_filter(co_authors: Dict[str, int], limit: int = 5) -> List[str]:
    co_author_list = sorted(co_authors.items(), key=lambda p: p[1], reverse=True)
    return [name for name, _ in co_author_list[:limit]]


def fetch_author_info(author: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    client = Client()
    papers_info = []
    co_authors: Dict[str, int] = {}
    print(f"{show_time()} Fetching Author Info: {author}")
    search = Search(query=f"au:{author}", max_results=10)
    for result in tqdm(
        client.results(search), desc="Processing Author Papers", unit="Paper"
    ):
        if author not in ", ".join(author.name for author in result.authors):
            continue
        author_list = [author.name for author in result.authors]
        co_authors = co_author_frequency(author, author_list, co_authors)
        paper_info = {
            "url": result.entry_id,
            "title": result.title,
            "abstract": result.summary,
            "authors": ", ".join(author.name for author in result.authors),
            "published": str(result.published).split(" ")[0],
            "updated": str(result.updated).split(" ")[0],
            "primary_cat": result.primary_category,
            "cats": result.categories,
        }
        papers_info.append(paper_info)
    co_author_names = co_author_filter(co_authors, limit=5)
    print(text_wrap("Num of Papers:"), len(papers_info))
    print(text_wrap("Num of Co-authors:"), len(co_author_names))
    return papers_info, co_author_names


def bfs(
    author_list: List[str], node_limit: int = 20
) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]], Dict]:
    graph = []
    node_feat: Dict[str, List[Dict[str, Any]]] = dict()
    edge_feat: Dict[str, List[Dict[str, Any]]] = dict()
    visit = []
    for author in author_list:
        if author in visit:
            continue
        papers_info, co_authors = fetch_author_info(author)
        if len(node_feat) <= node_limit:
            author_list.extend(co_authors)
            for co_au in co_authors:
                if (author, co_au) in graph or (co_au, author) in graph:
                    continue
                graph.append((author, co_au))
        visit.append(author)
        node_feat[author] = papers_info
    return graph, node_feat, edge_feat
