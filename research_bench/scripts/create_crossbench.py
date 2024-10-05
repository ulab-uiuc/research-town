import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Union, cast

import requests
from tqdm import tqdm


def extract_arxiv_id_from_url(url: str) -> Optional[str]:
    match = re.search(r'arxiv\.org/abs/(\d{4}\.\d{5})', url)
    if match:
        return match.group(1)
    else:
        return None


def get_paper_info(arxiv_id: str, max_retry: int = 5) -> Optional[Dict[str, Any]]:
    paper_id = f'ARXIV:{arxiv_id}'
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}'
    fields = 'title,authors,year,venue,abstract'
    headers = {'x-api-key': 'FfOnoChxCS2vGorFNV4sQB7KdzzRalp9ygKzAGf8'}
    params: Dict[str, Union[str, int]] = {
        'fields': fields,
    }

    for attempt in range(max_retry):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())
        else:
            time.sleep(5)
    return None


def get_references(arxiv_id: str, max_retry: int = 5) -> Optional[List[Dict[str, Any]]]:
    paper_id = f'ARXIV:{arxiv_id}'
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references'
    fields = 'title,abstract,year,venue,authors,externalIds,url,referenceCount,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy'
    params: Dict[str, Union[str, int]] = {
        'fields': fields,
        'limit': 100,
    }

    references: List[Any] = []
    offset = 0

    while True:
        params['offset'] = offset
        for attempt in range(max_retry):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' not in data or not data['data']:
                    return references
                for ref in data['data']:
                    references.append(ref['citedPaper'])
                if len(data['data']) < 100:
                    return references
                offset += 100
                break
            else:
                time.sleep(5)
        else:
            return references if references else None


def process_paper(arxiv_id: str) -> Optional[Dict[str, Any]]:
    paper_info = get_paper_info(arxiv_id)
    if not paper_info:
        return None

    references = get_references(arxiv_id)
    if references is None:
        references = []

    processed_references = []
    for ref in references:
        processed_ref = {
            'title': ref.get('title'),
            'abstract': ref.get('abstract'),
            'year': ref.get('year'),
            'venue': ref.get('venue'),
            'authors': [author.get('name') for author in ref.get('authors', [])],
            'externalIds': ref.get('externalIds'),
            'url': ref.get('url'),
            'referenceCount': ref.get('referenceCount'),
            'citationCount': ref.get('citationCount'),
            'influentialCitationCount': ref.get('influentialCitationCount'),
            'isOpenAccess': ref.get('isOpenAccess'),
            'fieldsOfStudy': ref.get('fieldsOfStudy'),
        }
        processed_references.append(processed_ref)

    paper_data = {
        'paper_title': paper_info.get('title'),
        'arxiv_id': arxiv_id,
        'authors': [author.get('name') for author in paper_info.get('authors', [])],
        'year': paper_info.get('year'),
        'venue': paper_info.get('venue'),
        'abstract': paper_info.get('abstract'),
        'references': processed_references,
    }

    return paper_data


def process_arxiv_links(input_file: str, output_file: str) -> None:
    if not os.path.exists(input_file):
        return

    with open(input_file, 'r') as f:
        urls = f.read().strip().split('\n')

    output_data = {}
    for url in tqdm(urls, desc='Processing arXiv links'):
        arxiv_id = extract_arxiv_id_from_url(url)
        if not arxiv_id:
            continue

        if arxiv_id in output_data:
            continue

        paper_data = process_paper(arxiv_id)
        if paper_data:
            output_data[paper_data['paper_title']] = paper_data
            time.sleep(5)
        else:
            print(f'can handle arXiv ID: {arxiv_id}')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)


def main() -> None:
    input_file = './arxiv_link.txt'
    output_file = '../benchmark/cross_bench.json'
    process_arxiv_links(input_file, output_file)


if __name__ == '__main__':
    main()
