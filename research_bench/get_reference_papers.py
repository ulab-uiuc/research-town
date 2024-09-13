import argparse
import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Union, cast

import requests
from tqdm import tqdm


def get_references(
    arxiv_id: str, offset: int = 0, limit: int = 100, max_retry: int = 5
) -> Optional[Dict[str, Any]]:
    """
    Fetch references for a given arXiv paper using the Semantic Scholar API with retry mechanism.

    Args:
        arxiv_id (str): The arXiv ID of the paper.
        offset (int): The offset for pagination. Default is 0.
        limit (int): The number of references to retrieve per request. Default is 100.
        max_retry (int): The maximum number of retries if the request fails. Default is 5.

    Returns:
        dict or None: The JSON response containing the references or None if the request failed after retries.
    """
    paper_id = f'ARXIV:{arxiv_id}'
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references'
    fields = 'title,abstract,year,venue,authors,externalIds,url,referenceCount,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy'
    params: Dict[str, Union[str, int]] = {
        'offset': offset,
        'limit': limit,
        'fields': fields,
    }

    for attempt in range(max_retry):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())
        else:
            print(
                f'Error fetching references for {paper_id}: {response.status_code}. Retrying {attempt + 1}/{max_retry}...'
            )
            time.sleep(5)  # Wait for 5 seconds before the next retry
    print(f'Failed to fetch references for {paper_id} after {max_retry} attempts.')
    return None


def get_all_references(arxiv_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all references for a given arXiv paper by handling pagination.

    Args:
        arxiv_id (str): The arXiv ID of the paper.

    Returns:
        list: A list of references for the paper.
    """
    all_references = []
    offset = 0
    while True:
        data = get_references(arxiv_id, offset)
        if data is None or not data.get('data'):
            break
        all_references.extend([ref['citedPaper'] for ref in data['data']])
        offset += len(data['data'])
        if len(data['data']) < 100:  # Less than the limit, so we've reached the end
            break
        time.sleep(
            5
        )  # Wait for 5 seconds before the next API call to avoid rate limits
    return all_references


def process_reference(ref: dict[str, Any]) -> dict[str, Any]:
    """
    Process a reference paper and extract key details.

    Args:
        ref (dict): The reference paper data.

    Returns:
        dict: A dictionary with processed reference data.
    """
    return {
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


def extract_arxiv_id(file_path: str) -> Optional[str]:
    """
    Extract the arXiv ID from a file path.

    Args:
        file_path (str): The file path of the downloaded PDF.

    Returns:
        str or None: The extracted arXiv ID or None if extraction fails.
    """
    match = re.search(r'(\d{4}\.\d{5})', file_path)
    if match:
        return match.group(1)
    else:
        print(f'Could not extract arXiv ID from {file_path}')
        return None


def process_papers(input_file: str, output_file: str) -> None:
    """
    Process papers from the input JSON file, fetch their references, and update the output JSON file.

    Args:
        input_file (str): Path to the input JSON file containing paper metadata.
        output_file (str): Path to the output JSON file to save the updated paper metadata with references.
    """
    # Read the existing input JSON file
    if os.path.exists(input_file):
        with open(input_file, 'r') as f:
            output_data = json.load(f)
    else:
        print(f'Error: Input file {input_file} does not exist.')
        return

    # Process each paper in the input file
    paper_titles = list(output_data.keys())
    for title in tqdm(paper_titles, desc='Processing papers'):
        data = output_data.get(title)
        pdf_path = data.get('pdf_path')
        if not pdf_path:
            print(f'Skipping {title} due to missing pdf_path')
            continue

        # Extract arXiv ID from the PDF path
        arxiv_id = extract_arxiv_id(pdf_path)
        if not arxiv_id:
            print(f'Skipping {title} due to invalid arXiv ID')
            continue

        # Fetch references only if they are not already stored
        if not data.get('references'):
            print(f'Processing {title} with arXiv ID: {arxiv_id}')
            references = get_all_references(arxiv_id)
            processed_references = [process_reference(ref) for ref in references]
            output_data[title]['references'] = processed_references
            time.sleep(5)  # Wait for 5 seconds before processing the next paper
        else:
            print(f'Skipping {title} as it already has references')

    # Write the updated data back to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f'Processing complete. Results saved in {output_file}')


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Fetch and process references for downloaded arXiv papers.'
    )

    # Input file argument (default: 'paper_info.json')
    parser.add_argument(
        '--input_file',
        type=str,
        default='paper_info.json',
        help="Path to the input JSON file containing downloaded paper metadata (Default: 'paper_info.json')",
    )

    # Output file argument (default: 'output_with_references.json')
    parser.add_argument(
        '--output_file',
        type=str,
        default='output_with_references.json',
        help="Path to the output JSON file to save the paper metadata with references (Default: 'output_with_references.json')",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main function to process papers and fetch their references.
    """
    # Parse command-line arguments
    args = parse_args()

    # Process papers and fetch references
    process_papers(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
