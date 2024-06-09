import chunk
import os
from sklearn.cluster import KMeans
import numpy as np
import openai
# from PyPDF2 import PdfReader
import faiss
from transformers import BertTokenizer, BertModel
import torch
import json
import time
from bert_score import score
import warnings
import copy
from tqdm import tqdm
import torch.nn.functional as F
import pickle
warnings.filterwarnings("ignore")
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
name='natural_language_processing'
tokenizer = BertTokenizer.from_pretrained('facebook/contriever')
model = BertModel.from_pretrained('facebook/contriever').to(torch.device("cpu"))
def get_bert_embedding(instructions):

    # tokenizer = BertTokenizer.from_pretrained("bert-base-uncased", ignore_mismatched_sizes=True)
    # model = BertModel.from_pretrained("bert-base-uncased", ignore_mismatched_sizes=True).to(torch.device("cpu"))

    # encoded_input_all = [tokenizer(text['instruction']+text['input'], return_tensors='pt').to(torch.device("cuda")) for text in instructions]

    encoded_input_all = [tokenizer(text, return_tensors='pt', truncation=True,
                                   max_length=512).to(torch.device("cpu")) for text in instructions]

    with torch.no_grad():
        emb_list = []
        for inter in encoded_input_all:
            emb = model(**inter)
            emb_list.append(emb['last_hidden_state'].mean(1))
    return emb_list


with open(name+'.json', 'r') as json_file:
    data = json.load(json_file)
agent_dict={}
for pk in data.keys():
    agent_dict[pk]=get_bert_embedding([data[pk]['abstract']])
with open(name+'.pkl', 'wb') as pkl_file:
    pickle.dump(agent_dict, pkl_file)