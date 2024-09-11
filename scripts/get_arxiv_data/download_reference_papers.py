import argparse
import json
import logging
import os
import re

import arxiv
from tqdm import tqdm


def setup_logging()->None:
    """Setup logging configuration."""
    logging.basicConfig(
        filename='download_reference_papers.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )

def extract_arxiv_id(file_path)->str:
    """
    Extract the arXiv ID from a file path using regex.

    Args:
        file_path (str): Path to the file.

    Returns:
        str or None: Extracted arXiv ID or None if extraction fails.
    """
    match = re.search(r'(\d{4}\.\d{5})', file_path)
    if match:
        return match.group(1)
    else:
        logging.error(f"Could not extract arXiv ID from {file_path}")
        return None

def download_pdf(arxiv_id, save_path)->bool:
    """
    Download an arXiv paper as a PDF by its arXiv ID.

    Args:
        arxiv_id (str): The arXiv ID of the paper.
        save_path (str): The path where the PDF should be saved.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        paper.download_pdf(filename=save_path)
        logging.info(f"Downloaded {arxiv_id} to {save_path}")
        return True
    except Exception as e:
        logging.error(f"Error downloading {arxiv_id}: {str(e)}")
        return False

def process_papers(input_file, output_file, base_save_dir)->None:
    """
    Process each paper, extract references, and download the referenced PDFs.

    Args:
        input_file (str): Path to input JSON file with paper metadata.
        output_file (str): Path to output JSON file where updated metadata will be saved.
        base_save_dir (str): Base directory where the reference PDFs will be saved.
    """
    # Read the existing output JSON file
    with open(input_file, 'r') as f:
        output_data = json.load(f)

    # Process each paper in the JSON file
    for title, data in tqdm(output_data.items(), desc="Processing papers"):
        arxiv_id = extract_arxiv_id(data.get('pdf_path'))
        data['arxiv_id'] = arxiv_id

        if not arxiv_id:
            logging.warning(f"Skipping {title} due to invalid arXiv ID")
            continue

        # Create a folder for references
        ref_folder = os.path.join(base_save_dir, f'{arxiv_id}_references')
        os.makedirs(ref_folder, exist_ok=True)

        # Process references
        arxiv_references = []
        for ref in tqdm(data.get('references', []), desc=f"Processing references for {arxiv_id}", leave=False):
            if not ref or not ref.get('externalIds'):
                continue
            ref_arxiv_id = ref.get('externalIds', {}).get('ArXiv')
            if ref_arxiv_id:
                pdf_path = os.path.join(ref_folder, f"{ref_arxiv_id}.pdf")
                if download_pdf(ref_arxiv_id, pdf_path):
                    arxiv_references.append({
                        'title': ref.get('title'),
                        'arxiv_id': ref_arxiv_id,
                        'pdf_path': pdf_path
                    })

        # Add arxiv_references to the paper data
        data['arxiv_references'] = arxiv_references

    # Write the updated data back to the output JSON file
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    logging.info(f"Processing complete. Results saved in {output_file}")


def parse_args()->argparse.Namespace:
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Download arXiv reference papers as PDFs.")
    
    parser.add_argument(
        '--input_file', 
        type=str, 
        required=True, 
        help="Path to the input JSON file containing paper metadata."
    )
    
    parser.add_argument(
        '--output_file', 
        type=str, 
        required=True, 
        help="Path to the output JSON file to save updated metadata."
    )
    
    parser.add_argument(
        '--save_dir', 
        type=str, 
        required=True, 
        help="Base directory where reference PDFs will be saved."
    )
    
    return parser.parse_args()


def main():
    """
    Main function to process papers and fetch their references.
    """
    # Setup logging
    setup_logging()

    # Parse command-line arguments
    args = parse_args()

    # Process papers and download reference PDFs
    process_papers(args.input_file, args.output_file, args.save_dir)


if __name__ == '__main__':
    main()