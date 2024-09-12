import argparse
import json
import os
from datetime import datetime, timedelta

import arxiv
import requests


def download_papers(keywords: str, start_date: str, end_date: str, save_dir: str)->None:
    """
    Downloads arXiv papers based on the search query and criteria.

    Args:
        keywords (str): The keywords to search for in the paper title or abstract.
        start_date (str): The start date for the search in YYYYMMDD format.
        end_date (str): The end date for the search in YYYYMMDD format.
        save_dir (str): The directory where the papers should be saved. 
    """
    # Construct the search query (in AI and Machine Learning categories)
    if len(keywords) == 0:
        search_query = f'cat:cs.AI OR cat:cs.LG'
    else:
        search_query = f'cat:cs.AI OR cat:cs.LG AND {keywords}'

    # Build the complete query string with date filter
    full_query = f'{search_query} AND submittedDate:[{start_date} TO {end_date}]'

    # Ensure the save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Perform the search on arXiv
    search = arxiv.Search(
        query=full_query,
        max_results=1000,  # Maximum number of results
        sort_by=arxiv.SortCriterion.SubmittedDate,  # Sort by submission date
        sort_order=arxiv.SortOrder.Descending  # Newest first
    )

    # Dictionary to store paper information (title, arXiv ID, file path)
    paper_info_dict = {}

    # Download papers that match the search query
    for paper in search.results():
        # Check if the title contains the keyword "agent" (case-insensitive)
        if 'agent' in paper.title.lower():
            try:
                # Get the URL of the PDF
                pdf_url = paper.pdf_url

                # Construct the file name with the paper's short ID
                file_name = f"{save_dir}/{paper.get_short_id()}.pdf"

                # Download the PDF
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    # Save the PDF to the specified directory
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {paper.title}")

                    # Add paper information to the dictionary
                    paper_info_dict[paper.title] = {
                        'paper_title': paper.title,
                        'arxiv_id': paper.get_short_id(),
                        'pdf_path': file_name
                    }
                else:
                    print(f"Failed to download: {paper.title} (Status Code: {response.status_code})")
            except Exception as e:
                print(f"Error downloading {paper.title}: {str(e)}")

    print("Download complete.")

    # Save the paper information dictionary to a JSON file
    json_file_path = os.path.join(save_dir, 'paper_info.json')
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(paper_info_dict, json_file, ensure_ascii=False, indent=4)

    print(f"Paper information saved to {json_file_path}")


def parse_args()->argparse.Namespace:
    """
    Parses command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments including keywords, start_date, end_date, and save_dir.
    """
    parser = argparse.ArgumentParser(description="Download AI-related papers from arXiv based on search criteria.")
    
    # Keywords argument (default: 'Large language models')
    parser.add_argument(
        '--keywords', 
        type=str, 
        default='Large language models', 
        help="Search keywords for paper titles and abstracts (Default: 'Large language models')"
    )
    
    # Start date argument (default: 30 days ago)
    parser.add_argument(
        '--start_date',
        type=str,
        default=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
        help="Start date for the search in YYYYMMDD format (Default: 30 days ago)"
    )

    # End date argument (default: today)
    parser.add_argument(
        '--end_date',
        type=str,
        default=datetime.now().strftime('%Y%m%d'),
        help="End date for the search in YYYYMMDD format (Default: today)"
    )

    # Save directory argument (default: 'AI_agent_papers')
    parser.add_argument(
        '--save_dir',
        type=str,
        default='./data/arxiv_AI_papers',
        help="Directory to save downloaded papers (Default: 'AI_agent_papers')"
    )

    return parser.parse_args()


def main()->None:
    """
    Main execution function that parses arguments and triggers the download process.
    """
    # Parse the command-line arguments
    args = parse_args()

    # Call the download function with the provided arguments
    download_papers(
        keywords=args.keywords,
        start_date=args.start_date,
        end_date=args.end_date,
        save_dir=args.save_dir
    )


if __name__ == '__main__':
    main()