from typing import Dict, List, Tuple

import arxiv
import faiss
import torch
from transformers import BertModel, BertTokenizer


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
