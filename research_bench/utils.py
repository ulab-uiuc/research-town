# common.py

import json
import os
import time
from typing import Any, Dict, List, Optional, Set

import arxiv
import requests

from research_town.utils.model_prompting import model_prompting

SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/'


def get_references(arxiv_id: str, max_retries: int = 5) -> List[Dict[str, Any]]:
    url = f'{SEMANTIC_SCHOLAR_API_URL}ARXIV:{arxiv_id}/references'
    params = {'limit': 100}
    headers = {'User-Agent': 'PaperProcessor/1.0'}

    for attempt in range(max_retries):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return [
                ref['citedPaper'] for ref in data.get('data', []) if 'citedPaper' in ref
            ]
        else:
            wait_time = 2**attempt
            print(
                f'Error {response.status_code} fetching references for {arxiv_id}. Retrying in {wait_time}s...'
            )
            time.sleep(wait_time)  # Exponential backoff
    print(f'Failed to fetch references for {arxiv_id} after {max_retries} attempts.')
    return []


def get_paper_by_keyword(
    keyword: str, existing_arxiv_ids: Set[str], max_papers: int = 10
) -> List[arxiv.Result]:
    query = f'all:"{keyword}" AND (cat:cs.AI OR cat:cs.LG)'
    search = arxiv.Search(
        query=query,
        max_results=max_papers * 2,  # Fetch extra to account for duplicates
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    papers = []
    for paper in search.results():
        short_id = paper.get_short_id()
        if short_id not in existing_arxiv_ids:
            papers.append(paper)
            existing_arxiv_ids.add(short_id)
        if len(papers) >= max_papers:
            break
    return papers


def save_benchmark(benchmark: Dict[str, Any], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark, f, indent=4, ensure_ascii=False)
    print(f'Benchmark saved to {output_path}')


def get_paper_by_arxiv_id(arxiv_id: str) -> Optional[arxiv.Result]:
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(search.results())
        return results[0] if results else None
    except Exception as e:
        print(f'Error fetching paper {arxiv_id}: {e}')
        return None


def process_paper(paper: arxiv.Result) -> Dict[str, Any]:
    arxiv_id = paper.get_short_id()
    references = get_references(arxiv_id)
    return {
        'title': paper.title,
        'arxiv_id': arxiv_id,
        'authors': [author.name for author in paper.authors],
        'abstract': paper.summary,
        'published': paper.published.isoformat(),
        'updated': paper.updated.isoformat(),
        'references': references,
    }


def single_agent_proposal_writing(
    intros: List[str], model: str = 'gpt-4o-mini'
) -> Optional[str]:
    combined_intro = '\n\n'.join(intros)
    prompt = [
        {
            'role': 'user',
            'content': f"""You are a skilled research assistant with extensive experience in academic writing and research proposal development. Please write a research proposal abstract based on the following ideas and external data.
The proposal should be structured to answer five core questions. The proposal should be structured to answer five core questions, with each answer clearly labeled in the format: [Question X], where X is the question number (1 to 5). Each answer should be full of details and reasoning and directly address the question.

Here are the five core questions:

[Question 1] - What is the problem?

Formulate the specific research question you aim to address. Only output one question and do not include any more information.

[Question 2] - Why is it interesting and important?

Explain the broader implications of solving this problem for the research community.
Discuss how such paper will affect the future research.
Discuss how addressing this question could advance knowledge or lead to practical applications.

[Question 3] - Why is it hard?

Discuss the challenges and complexities involved in solving this problem.
Explain why naive or straightforward approaches may fail.
Identify any technical, theoretical, or practical obstacles that need to be overcome. MAKE IT CLEAR.

[Question 4] - Why hasn't it been solved before?

Identify gaps or limitations in previous research or existing solutions.
Discuss any barriers that have prevented this problem from being solved until now.
Explain how your approach differs from or improves upon prior work. MAKE IT CLEAR.

[Question 5] - What are the key components of my approach and results?

Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use.
Describe the expected outcomes. MAKE IT CLEAR.

Your goal is to ensure the proposal is clear, concise, and logically structured.
Now you will be given a set of introduction texts from various sources. Please use this information to generate a comprehensive research proposal based on the introductions, you need to look into what future research directions, topics or methods could be use for the proposal writing.

Here are the introduction texts: {combined_intro}

The proposal should be structured to answer five core questions, with each answer clearly labeled in the format: [Question X], where X is the question number (1 to 5).

For example:
[Question 1]: ....
[Question 2]: ....
[Question 3]: ....
[Question 4]: ....
[Question 5]: ....

Now, let's begin:""",
        }
    ]

    try:
        response = model_prompting(model, prompt)
        return response[0] if response and response[0] else None
    except Exception as e:
        print(f'Error generating proposal: {e}')
        return None

def get_current_5q(intro: str, model:str = 'gpt-4o-mini') -> Optional[str]:
    """
    Generates the five core research questions based on the introduction text using an LLM.

    Args:
        intro (str): Introduction text of the paper.

    Returns:
        Optional[str]: Generated five core questions as a string.
    """
    try:
        prompt = [
            {
                'role': 'user',
                'content': (
                    'Here is a high-level summarized insight of a research field Machine Learning.\n\n'
                    'Here are the five core questions:\n\n'
                    '[Question 1] - What is the problem?\n\n'
                    'Formulate the specific research question you aim to address. Only output one question and do not include any more information.\n\n'
                    '[Question 2] - Why is it interesting and important?\n\n'
                    'Explain the broader implications of solving this problem for the research community.\n'
                    'Discuss how such paper will affect the future research.\n'
                    'Discuss how addressing this question could advance knowledge or lead to practical applications.\n\n'
                    '[Question 3] - Why is it hard?\n\n'
                    'Discuss the challenges and complexities involved in solving this problem.\n'
                    'Explain why naive or straightforward approaches may fail.\n'
                    'Identify any technical, theoretical, or practical obstacles that need to be overcome. MAKE IT CLEAR.\n\n'
                    "[Question 4] - Why hasn't it been solved before?\n\n"
                    'Identify gaps or limitations in previous research or existing solutions.\n'
                    'Discuss any barriers that have prevented this problem from being solved until now.\n'
                    'Explain how your approach differs from or improves upon prior work. MAKE IT CLEAR.\n\n'
                    '[Question 5] - What are the key components of my approach and results?\n\n'
                    'Outline your proposed methodology in detail, including the method, dataset, metric that you plan to use.\n'
                    'Describe the expected outcomes. MAKE IT CLEAR.\n\n'
                    f'Introduction:\n{intro}\n\n'
                    'Please provide the five core questions contents based on the above introduction.'
                ),
            }
        ]
        response = model_prompting(model, prompt, mode='TEST')
        if response and len(response) > 0 and len(response[0]) > 0:
            return response[0]
        else:
            print(
                'Received empty response from model_prompting for current_5q.'
            )
            return None
    except Exception as e:
        print(f'Error generating current_5q: {e}')
        return None