import argparse
from typing import List

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import get_url_from_title


def fetch_paper_titles(url: str) -> List[str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    html_titles = soup.find_all('a')
    titles = [title.get_text() for title in html_titles if title.get_text()]
    return titles


def save_paper_urls(titles: List[str], output_file: str) -> None:
    with open(output_file, 'a') as f:
        for title in tqdm(titles):
            url = get_url_from_title(title)
            if url:
                f.write(f'{url}\n')


def main() -> None:
    parser = argparse.ArgumentParser(description='Scrape and save NeurIPS paper URLs.')
    parser.add_argument(
        '--url',
        type=str,
        default='https://nips.cc/virtual/2024/papers.html?filter=titles',
        help='URL of the NeurIPS paper list',
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./mlbench/mlbench_paper_links.txt',
        help='Output file to save the paper URLs',
    )

    args = parser.parse_args()
    print(f'Fetching paper titles from {args.url}...')
    titles = fetch_paper_titles(args.url)

    print(f'Saving paper URLs to {args.output}...')
    save_paper_urls(titles, args.output)

    print('Done!')


if __name__ == '__main__':
    main()
