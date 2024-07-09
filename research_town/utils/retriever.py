from typing import List

import torch
from transformers import BertModel, BertTokenizer


def get_embedding(
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
