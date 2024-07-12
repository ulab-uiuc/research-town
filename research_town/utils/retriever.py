from typing import List

import torch
from transformers import BertModel, BertTokenizer


def get_embed(
    instructions: List[str],
    retriever_tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
        'facebook/contriever'
    ),
    retriever_model: BertModel = BertModel.from_pretrained('facebook/contriever'),
) -> List[torch.Tensor]:
    encoded_input_all = [
        retriever_tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        for text in instructions
    ]
    with torch.no_grad():
        emb_list = []
        for inter in encoded_input_all:
            emb = retriever_model(**inter)
            emb_list.append(emb['last_hidden_state'].mean(1))
    return emb_list


def rank_topk(
    query_embed: List[torch.Tensor], corpus_embed: List[torch.Tensor], num: int
) -> List[List[int]]:
    xq = torch.cat(query_embed, 0)
    xb = torch.cat(corpus_embed, 0)

    xq = torch.nn.functional.normalize(xq, p=2, dim=1)
    xb = torch.nn.functional.normalize(xb, p=2, dim=1)

    similarity = torch.mm(xq, xb.t())

    _, indices = torch.topk(similarity, num, dim=1, largest=True)
    list_of_list_indices: List[List[int]] = indices.tolist()
    return list_of_list_indices
