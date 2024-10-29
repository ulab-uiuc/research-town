import argparse
import os
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
    urls = []
    if not os.path.exists(output_file):
        open(output_file, 'w').close()

    with open(output_file, 'a') as f:
        for title in tqdm(titles):
            url = get_url_from_title(title)
            if url and url not in urls:
                f.write(f'{url}\n')
                urls.append(url)


def save_latest_paper_urls(
    output_file_full: str, output_file_latest: str, paper_num: int
) -> None:
    if not os.path.exists(output_file_full):
        open(output_file_full, 'w').close()

    with open(output_file_full, 'r') as f:
        lines = f.readlines()
    lines = list(set(lines))
    lines.sort()
    lines = lines[-paper_num:]
    with open(output_file_latest, 'w') as f:
        for line in lines:
            f.write(line)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Scrape and save conference paper URLs.'
    )
    parser.add_argument(
        '--conference',
        type=str,
        default='iclr',
        choices=['iclr', 'nips'],
        help='Conference name, e.g., iclr or nips',
    )
    parser.add_argument(
        '--url',
        type=str,
        help='URL of the conference paper list',
    )
    parser.add_argument(
        '--output_full',
        type=str,
        help='Output file to save the paper URLs',
    )
    parser.add_argument(
        '--output_latest',
        type=str,
        help='Output file to save the latest paper URLs',
    )
    parser.add_argument(
        '--latest_paper_num',
        type=int,
        default=100,
        help='Number of latest papers to save',
    )

    args = parser.parse_args()

    if not args.url:
        args.url = (
            f'https://{args.conference}.cc/virtual/2024/papers.html?filter=titles'
        )
    if not args.output_full:
        args.output_full = f'./{args.conference}bench/{args.conference}_paper_links.txt'
    if not args.output_latest:
        args.output_latest = (
            f'./{args.conference}bench/{args.conference}_paper_links_latest.txt'
        )

    print(f'Fetching paper titles from {args.url}...')
    titles = fetch_paper_titles(args.url)

    print(f'Saving paper URLs to {args.output_full}...')
    save_paper_urls(titles, args.output_full)

    save_latest_paper_urls(args.output_full, args.output_latest, args.latest_paper_num)
    print('Done!')


if __name__ == '__main__':
    main()
