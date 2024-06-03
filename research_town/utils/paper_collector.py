import datetime
from xml.etree import ElementTree

import arxiv
import faiss
import requests
import torch
from beartype.typing import Any, Dict, List, Tuple
from transformers import BertModel, BertTokenizer

ATOM_NAMESPACE = '{http://www.w3.org/2005/Atom}'


def get_related_papers(corpus: List[str], query: str, num: int) -> List[str]:
    corpus_embedding = get_bert_embedding(corpus)
    query_embedding = get_bert_embedding([query])
    indices = neiborhood_search(corpus_embedding, query_embedding, num)
    related_papers = [corpus[idx] for idx in indices[0].tolist()]
    return related_papers


def get_bert_embedding(instructions: List[str]) -> List[torch.Tensor]:
    tokenizer = BertTokenizer.from_pretrained('facebook/contriever')
    model = BertModel.from_pretrained('facebook/contriever').to(torch.device('cpu'))

    encoded_input_all = [
        tokenizer(text, return_tensors='pt', truncation=True, max_length=512).to(
            torch.device('cpu')
        )
        for text in instructions
    ]

    with torch.no_grad():
        emb_list = []
        for inter in encoded_input_all:
            emb = model(**inter)
            emb_list.append(emb['last_hidden_state'].mean(1))
    return emb_list


def neiborhood_search(
    query_data: List[torch.Tensor], corpus_data: List[torch.Tensor], num: int
) -> Any:
    d = 768
    neiborhood_num = num
    xq = torch.cat(query_data, 0).cpu().numpy()
    xb = torch.cat(corpus_data, 0).cpu().numpy()
    index = faiss.IndexFlatIP(d)
    xq = xq.astype('float32')
    xb = xb.astype('float32')
    faiss.normalize_L2(xq)
    faiss.normalize_L2(xb)
    index.add(xb)  # add vectors to the index
    data, index = index.search(xq, neiborhood_num)
    return index


def find_text(element: ElementTree.Element, path: str) -> str:
    found_element = element.find(path)
    if found_element is not None and found_element.text is not None:
        return found_element.text.strip()
    return ''


def get_daily_papers(
    topic: str, query: str = 'slam', max_results: int = 2
) -> Tuple[Dict[str, Dict[str, List[str]]], str]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = client.results(search)
    content: Dict[str, Dict[str, List[str]]] = {}
    newest_day = ''
    for result in results:
        paper_title = result.title
        paper_url = result.entry_id
        paper_abstract = result.summary.replace('\n', ' ')
        publish_time = result.published.date()
        newest_day = publish_time
        if publish_time in content:
            content[publish_time]['abstract'].append(
                paper_title + ': ' + paper_abstract
            )
            content[publish_time]['info'].append(paper_title + ': ' + paper_url)
        else:
            content[publish_time] = {}
            content[publish_time]['abstract'] = [paper_title + ': ' + paper_abstract]
            content[publish_time]['info'] = [paper_title + ': ' + paper_url]
    return content, newest_day


def get_papers(
    entries: List[ElementTree.Element], author_name: str
) -> Tuple[List[Dict[str, Any]], Dict[int, List[ElementTree.Element]]]:
    papers_list: List[Dict[str, Any]] = []
    papers_by_year: Dict[int, List[ElementTree.Element]] = {}

    for entry in entries:
        title = find_text(entry, f'{ATOM_NAMESPACE}title')
        published = find_text(entry, f'{ATOM_NAMESPACE}published')
        abstract = find_text(entry, f'{ATOM_NAMESPACE}summary')
        authors_elements = entry.findall(f'{ATOM_NAMESPACE}author')
        authors = [
            find_text(author, f'{ATOM_NAMESPACE}name') for author in authors_elements
        ]
        link = find_text(entry, f'{ATOM_NAMESPACE}id')

        if author_name in authors:
            coauthors = [author for author in authors if author != author_name]
            coauthors_str = ', '.join(coauthors)

            papers_list.append(
                {
                    'date': published,
                    'Title & Abstract': f'{title}; {abstract}',
                    'coauthors': coauthors_str,
                    'link': link,
                }
            )

            published_date = published
            date_obj = datetime.datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ')
            year = date_obj.year
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(entry)

    return papers_list, papers_by_year


def select_papers(
    papers_by_year: Dict[int, List[ElementTree.Element]], author_name: str
) -> List[Dict[str, Any]]:
    papers_list: List[Dict[str, Any]] = []

    for cycle_start in range(min(papers_by_year), max(papers_by_year) + 1, 5):
        cycle_end = cycle_start + 4
        for year in range(cycle_start, cycle_end + 1):
            if year in papers_by_year:
                selected_papers = papers_by_year[year][:2]
                for paper in selected_papers:
                    title = find_text(paper, f'{ATOM_NAMESPACE}title')
                    abstract = find_text(paper, f'{ATOM_NAMESPACE}summary')
                    authors_elements = paper.findall(f'{ATOM_NAMESPACE}author')
                    co_authors = [
                        find_text(author, f'{ATOM_NAMESPACE}name')
                        for author in authors_elements
                        if find_text(author, f'{ATOM_NAMESPACE}name') != author_name
                    ]

                    papers_list.append(
                        {
                            'Author': author_name,
                            'Title & Abstract': f'{title}; {abstract}',
                            'Date Period': f'{year}',
                            'Cycle': f'{cycle_start}-{cycle_end}',
                            'Co_author': ', '.join(co_authors),
                        }
                    )
    return papers_list


def get_paper_list(author_name: str) -> List[Dict[str, Any]]:
    author_query = author_name.replace(' ', '+')
    url = f'http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300'

    response = requests.get(url)

    if response.status_code == 200:
        xml_content = response.content.decode('utf-8', errors='ignore')
        root = ElementTree.fromstring(xml_content)
        entries = root.findall(f'{ATOM_NAMESPACE}entry')

        papers_list, papers_by_year = get_papers(entries, author_name)
        if len(papers_list) > 40:
            papers_list = select_papers(papers_by_year, author_name)

        # Trim the list to the 10 most recent papers
        papers_list = papers_list[:10]
        return papers_list
    else:
        print('Failed to fetch data from arXiv.')
        return []
