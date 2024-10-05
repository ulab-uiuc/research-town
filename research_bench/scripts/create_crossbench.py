import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Union, cast

import requests
from tqdm import tqdm


def extract_arxiv_id_from_url(url: str) -> Optional[str]:
    """
    从 arXiv 链接中提取 arXiv ID。

    Args:
        url (str): arXiv 论文链接，例如 "https://arxiv.org/abs/2402.13448"

    Returns:
        str 或 None: 提取的 arXiv ID 或者 None（如果提取失败）
    """
    match = re.search(r'arxiv\.org/abs/(\d{4}\.\d{5})', url)
    if match:
        return match.group(1)
    else:
        print(f'无法从链接中提取 arXiv ID: {url}')
        return None


def get_paper_info(arxiv_id: str, max_retry: int = 5) -> Optional[Dict[str, Any]]:
    """
    使用 Semantic Scholar API 获取论文的详细信息。

    Args:
        arxiv_id (str): 论文的 arXiv ID，例如 "2402.13448"
        max_retry (int): 最大重试次数，默认为 5

    Returns:
        dict 或 None: 论文的 JSON 数据，或者在重试失败后返回 None
    """
    paper_id = f'ARXIV:{arxiv_id}'
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}'
    fields = 'title,authors,year,venue,abstract'
    headers = {
        "x-api-key": "FfOnoChxCS2vGorFNV4sQB7KdzzRalp9ygKzAGf8"
    }
    params: Dict[str, Union[str, int]] = {
        'fields': fields,
    }

    for attempt in range(max_retry):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())
        else:
            print(
                f'获取论文信息时出错 {paper_id}: 状态码 {response.status_code}. 正在重试 {attempt + 1}/{max_retry}...'
            )
            time.sleep(5)  # 重试前等待5秒
    print(f'在 {max_retry} 次尝试后，仍无法获取论文 {paper_id} 的信息。')
    return None


def get_references(arxiv_id: str, max_retry: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    使用 Semantic Scholar API 获取论文的引用信息。

    Args:
        arxiv_id (str): 论文的 arXiv ID，例如 "2402.13448"
        max_retry (int): 最大重试次数，默认为 5

    Returns:
        list 或 None: 引用的论文列表，或者在重试失败后返回 None
    """
    paper_id = f'ARXIV:{arxiv_id}'
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references'
    fields = 'title,abstract,year,venue,authors,externalIds,url,referenceCount,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy'
    params: Dict[str, Union[str, int]] = {
        'fields': fields,
        'limit': 100,  # 每次请求获取100条引用
    }

    references = []
    offset = 0

    while True:
        params['offset'] = offset
        for attempt in range(max_retry):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' not in data or not data['data']:
                    return references  # 无更多引用
                for ref in data['data']:
                    references.append(ref['citedPaper'])
                if len(data['data']) < 100:
                    return references  # 已获取所有引用
                offset += 100
                break  # 成功获取当前批次，继续下一批
            else:
                print(
                    f'获取引用时出错 {paper_id}: 状态码 {response.status_code}. 正在重试 {attempt + 1}/{max_retry}...'
                )
                time.sleep(5)  # 重试前等待5秒
        else:
            print(f'在 {max_retry} 次尝试后，仍无法获取引用信息。')
            return references if references else None


def process_paper(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """
    处理单篇论文，获取其信息及引用。

    Args:
        arxiv_id (str): 论文的 arXiv ID，例如 "2402.13448"

    Returns:
        dict 或 None: 处理后的论文数据，或者在获取失败后返回 None
    """
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
    """
    处理 arXiv 链接文件，获取每篇论文的信息及引用，并保存为 JSON 文件。

    Args:
        input_file (str): 输入文件路径，例如 'arxivlink.txt'
        output_file (str): 输出文件路径，例如 'output_with_references.json'
    """
    if not os.path.exists(input_file):
        print(f'错误: 输入文件 {input_file} 不存在。')
        return

    with open(input_file, 'r') as f:
        urls = f.read().strip().split('\n')

    output_data = {}
    for url in tqdm(urls, desc='处理 arXiv 链接'):
        arxiv_id = extract_arxiv_id_from_url(url)
        if not arxiv_id:
            continue

        if arxiv_id in output_data:
            print(f'跳过重复的 arXiv ID: {arxiv_id}')
            continue

        print(f'正在处理 arXiv ID: {arxiv_id}')
        paper_data = process_paper(arxiv_id)
        if paper_data:
            output_data[paper_data['paper_title']] = paper_data
            # 为避免超过 API 限制，添加延时
            time.sleep(5)
        else:
            print(f'未能处理 arXiv ID: {arxiv_id}')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f'处理完成。结果已保存至 {output_file}。')




def main() -> None:
    """
    主函数，执行论文处理流程。
    """
    input_file = './arxiv_link.txt'
    output_file = '../benchmark/cross_bench.json'
    process_arxiv_links(input_file, output_file)


if __name__ == '__main__':
    main()