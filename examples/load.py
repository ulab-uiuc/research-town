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
import itertools
import time
from bert_score import score
import warnings
import copy
from tqdm import tqdm
import torch.nn.functional as F
import pickle

with open('graph_neural_networks_Mixtral_8_7B_saved_data'+'.json', 'r') as json_file:
    data = json.load(json_file)

# data_=dict(itertools.islice(data.items(), 10))
#
# with open('graph_neural_networks_Mixtral_8_7B_saved_data'+'.json', 'w') as json_file_:
#     json.dump(data_,json_file_)
a=1