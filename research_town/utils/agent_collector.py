from arxiv import Client, Search
from beartype.typing import Any, Dict, List, Tuple
from tqdm import tqdm

import requests
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



def get_authors(authors: List[str], first_author: bool = False) -> str:
    if first_author:
        return authors[0]
    return ', '.join(authors)


def author_position(author: str, author_list: List[str]) -> int:
    for ind, i in enumerate(author_list):
        if author.lower() == i.lower():
            return ind + 1

    return -1


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
    search = Search(query=f'au:{author}', max_results=10)
    for result in tqdm(
        client.results(search), desc='Processing Author Papers', unit='Paper'
    ):
        if author not in ', '.join(author.name for author in result.authors):
            continue
        author_list = [author.name for author in result.authors]
        co_authors = co_author_frequency(author, author_list, co_authors)
        paper_info = {
            'url': result.entry_id,
            'title': result.title,
            'abstract': result.summary,
            'authors': ', '.join(author.name for author in result.authors),
            'published': str(result.published).split(' ')[0],
            'updated': str(result.updated).split(' ')[0],
            'primary_cat': result.primary_category,
            'cats': result.categories,
        }
        papers_info.append(paper_info)
    co_author_names = co_author_filter(co_authors, limit=5)
    return papers_info, co_author_names


def bfs(
    author_list: List[str], node_limit: int = 20
) -> Tuple[
    List[Tuple[str, str]],
    Dict[str, List[Dict[str, Any]]],
    Dict[str, List[Dict[str, Any]]],
]:
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


def get_user_profile(author_name):
        author_query = author_name.replace(" ", "+")
        url = f"http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300"
        
        response = requests.get(url)
        papers_list = []
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')

            total_papers = 0
            data_to_save = []

            papers_by_year = {}

            for entry in entries:

                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                published = entry.find('{http://www.w3.org/2005/Atom}published').text.strip()
                abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                authors_elements = entry.findall('{http://www.w3.org/2005/Atom}author')
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors_elements]
                link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()  # Get the paper link

                # Check if the specified author is exactly in the authors list
                if author_name in authors:
                    # Remove the specified author from the coauthors list for display
                    coauthors = [author for author in authors if author != author_name]
                    coauthors_str = ", ".join(coauthors)

                    papers_list.append({
                        "date": published,
                        "Title & Abstract": f"{title}; {abstract}",
                        "coauthors": coauthors_str,
                        "link": link  # Add the paper link to the dictionary
                    })
                authors_elements = entry.findall('{http://www.w3.org/2005/Atom}author')
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors_elements]

                if author_name in authors:
                    # print(author_name)
                    # print(authors)
                    total_papers += 1
                    published_date = entry.find('{http://www.w3.org/2005/Atom}published').text.strip()
                    date_obj = datetime.datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ')

                    year = date_obj.year
                    if year not in papers_by_year:
                        papers_by_year[year] = []
                    papers_by_year[year].append(entry)

            if total_papers > 40:
                for cycle_start in range(min(papers_by_year), max(papers_by_year) + 1, 5):
                    cycle_end = cycle_start + 4
                    for year in range(cycle_start, cycle_end + 1):
                        if year in papers_by_year:
                            selected_papers = papers_by_year[year][:2]
                            for paper in selected_papers:
                                title = paper.find('{http://www.w3.org/2005/Atom}title').text.strip()
                                abstract = paper.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                                authors_elements = paper.findall('{http://www.w3.org/2005/Atom}author')
                                co_authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in
                                              authors_elements if
                                              author.find('{http://www.w3.org/2005/Atom}name').text != author_name]

                                papers_list.append({
                                    "Author": author_name,
                                    "Title & Abstract": f"{title}; {abstract}",
                                    "Date Period": f"{year}",
                                    "Cycle": f"{cycle_start}-{cycle_end}",
                                    "Co_author": ", ".join(co_authors)
                                })

            papers_list = papers_list[:10]
            personal_info = "; ".join([f"{details['Title & Abstract']}" for details in papers_list])
            info = summarize_research_direction(personal_info)
            return info
        else:
            print("Failed to fetch data from arXiv.")
            return ""
        
def summarize_research_field(profile, keywords, dataset, data_embedding):
    # papers = paperinfo(dataset)
    
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