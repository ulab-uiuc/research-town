import os
import json
import datetime
from xml.etree import ElementTree
import requests
import openai
import time
import faiss
from transformers import BertTokenizer, BertModel
import torch
import copy
import datetime
import json
import arxiv

KEY = "TOGETHER_API_KEY"
openai.api_base = 'https://api.together.xyz'
llm_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"


def show_time():
    time_stamp = '\033[1;31;40m[' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ']\033[0m'

    return time_stamp


def text_wrap(text):
    return '\033[1;31;40m' + str(text) + '\033[0m'


def write_to_json(data, output_file):
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def count_entries_in_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return len(data)


def clean_title(title):
    cleaned_title = title.replace("\n", " ").strip()
    cleaned_title = os.path.splitext(cleaned_title)[0]
    cleaned_title = cleaned_title.replace(":", "").replace("- ", " ").replace("-", " ").replace("_", " ").title()

    return cleaned_title

def get_bert_embedding(instructions):
    tokenizer = BertTokenizer.from_pretrained('facebook/contriever')
    model = BertModel.from_pretrained('facebook/contriever').to(torch.device("cpu"))

    # encoded_input_all = [tokenizer(text['instruction']+text['input'], return_tensors='pt').to(torch.device("cuda")) for text in instructions]

    encoded_input_all = [tokenizer(text, return_tensors='pt', truncation=True,
                                   max_length=512).to(torch.device("cpu")) for text in instructions]

    with torch.no_grad():
        emb_list = []
        for inter in encoded_input_all:
            emb = model(**inter)
            emb_list.append(emb['last_hidden_state'].mean(1))
    return emb_list

def neiborhood_search(corpus_data, query_data, num=8):
    d = 768  # dimension
    neiborhood_num = num
    xq = torch.cat(query_data, 0).cpu().numpy()
    xb = torch.cat(corpus_data, 0).cpu().numpy()
    index = faiss.IndexFlatIP(d)
    xq = xq.astype('float32')
    xb = xb.astype('float32')
    faiss.normalize_L2(xq)
    faiss.normalize_L2(xb)
    index.add(xb)  # add vectors to the index
    D, I = index.search(xq, neiborhood_num)

    return I

#######
def summarize_research_field(profile, keywords, dataset, data_embedding):
    # papers = paperinfo(dataset)
    prompt_qa = (
        "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgounds and trends in this field (related to my profile if possible)."
        "Here is my profile: {profile}"
        "Here are the keywords: {keywords}"
        "Here are the retrieved paper abstracts: {papers}"
    )
    query_format = (
        "Given the profile of me, keywords, some recent paper titles and abstracts. Could you summarize the keywords of high level research backgounds and trends in this field (related to my profile if possible)."
        "Here is my profile: {profile}"
        "Here are the keywords: {keywords}"
    )
    openai.api_key = KEY
    content_l = []
    input = {}
    input['profile'] = profile
    input['keywords'] = keywords

    query_input = {}
    query_input['profile'] = profile
    query_input['keywords'] = keywords

    query = query_format.format_map(query_input)

    query_embedding = get_bert_embedding([query])
    # text_chunk_l = dataset
    text_chunk_l = []

    # with open(dataset_path, 'r', encoding='utf-8') as file:
    #     dataset = json.load(file)
    title_chunk = []
    data_embedding_l = []
    for k in dataset.keys():
        # import pdb
        # pdb.set_trace()
        title_chunk.extend(dataset[k]['info'])
        text_chunk_l.extend(dataset[k]['abstract'])
        data_embedding_l.extend(data_embedding[k])
    # import pdb
    # pdb.set_trace()
    chunks_embedding_text_all = data_embedding_l
    ch_text_chunk = copy.copy(text_chunk_l)
    ch_text_chunk_embed = copy.copy(chunks_embedding_text_all)
    num_chunk = 10
    # print("raw_chunk_length: ", raw_chunk_length)

    neib_all = neiborhood_search(ch_text_chunk_embed, query_embedding, num_chunk)
    neib_all = neib_all.reshape(-1)

    context = []
    retrieve_paper = []

    for i in neib_all:
        context.append(ch_text_chunk[i])
        # if i not in retrieve_paper:
        retrieve_paper.append(title_chunk[i])
    # import pdb
    # pdb.set_trace()
    input['papers'] = '; '.join(context)
    prompt = prompt_qa.format_map(input)
    # import pdb
    # pdb.set_trace()
    # import pdb
    # pdb.set_trace()

    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt}], max_tokens=512)
    except:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt}], max_tokens=512)
    content = completion.choices[0].message["content"]
    content_l.append(content)
    return content_l, retrieve_paper

def generate_ideas(trend):
    prompt_qa = (
       "Here is a high-level summarized trend of a research field {trend}."
       "How do you view this field? Do you have any novel ideas or insights?"
       "Please give me 3 to 5 novel ideas and insights in bullet points. Each bullet points should be concise, containing 2 or 3 sentences."
    )

    openai.api_key = KEY
    content_l = []
    input = {}
    # input['profile'] = profile
    input['trend'] = trend
    prompt = prompt_qa.format_map(input)
    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt}], temperature=0,seed = 42, top_p=0)
    except:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt}], temperature=0,seed = 42, top_p=0)
    content = completion.choices[0].message["content"]
    content_l.append(content)
    return content_l

def summarize_research_direction(personal_info):
    prompt_qa = (
    "Based on the list of the researcher's first person persona from different times, please write a comprehensive first person persona. Focus more on more rescent personas. Be concise and clear (around 300 words)."
    "Here are the personas from different times: {peronalinfo}"
    )

    openai.api_key = KEY
    content_l = []
    input = {}
    input['peronalinfo'] = personal_info
    prompt = prompt_qa.format_map(input)
    try:
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt}], temperature=0,seed = 42, top_p=0)
    except:
        time.sleep(20)
        completion = openai.ChatCompletion.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": prompt}], temperature=0,seed = 42, top_p=0)
    content = completion.choices[0].message["content"]
    content_l.append(content)
    return content_l

def get_authors(authors, first_author = False):
    output = str()
    if first_author == False:
        output = ", ".join(str(author) for author in authors)
    else:
        output = authors[0]
    return output

def get_daily_papers(topic, query="slam", max_results=2):
    """
    @param topic: str
    @param query: str
    @return paper_with_code: dict
    """

    # output
    content = dict()
    Info = dict()
    search_engine = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    newest_day = ""
    for result in search_engine.results():

        paper_id = result.get_short_id()
        paper_title = result.title
        paper_url = result.entry_id
        # paper_abstract = result.summary

        paper_abstract = result.summary.replace("\n", " ")
        paper_authors = get_authors(result.authors)
        paper_first_author = get_authors(result.authors, first_author=True)
        primary_category = result.primary_category

        publish_time = result.published.date()
        newest_day = publish_time
        # print("Time = ", publish_time ,
        #       " title = ", paper_title,
        #       " author = ", paper_first_author)

        # eg: 2108.09112v1 -> 2108.09112
        # ver_pos = paper_id.find('v')
        # if ver_pos == -1:
        #     paper_key = paper_id
        # else:
        #     paper_key = paper_id[0:ver_pos]
        if publish_time in content:
            content[publish_time]['abstract'].append(paper_title + ": " + paper_abstract)
            content[publish_time]['info'].append(paper_title + ": " + paper_url)
            # Info[publish_time].append(paper_title+": "+paper_url)
        else:
            content[publish_time] = {}
            content[publish_time]['abstract'] = [paper_title + ": " + paper_abstract]
            content[publish_time]['info'] = [paper_title + ": " + paper_url]
            # content[publish_time] = [paper_abstract]
            # Info[publish_time] =
        # print(publish_time)
        # content[paper_key] = f"|**{publish_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|\n"
    data = content

    return data, newest_day