# ArXiv Paper Downloader and Reference Fetcher

This repository contains three Python scripts that automate the process of downloading papers from ArXiv, fetching their references, and downloading the referenced papers as well.

## Scripts Overview

1. **`download_arxiv_papers.py`**:
   - Downloads papers from ArXiv based on specified keywords and date ranges, and saves them as PDFs along with a JSON file containing metadata.

2. **`get_reference_papers.py`**:
   - Fetches the references for each downloaded ArXiv paper using the Semantic Scholar API and updates the JSON file (`paper_info.json`) with reference details.

3. **`download_reference_papers.py`**:
   - Downloads the PDFs of the referenced papers from ArXiv based on the references fetched in the previous step, and saves them in a structured directory.

## How to Run

To automate the entire process, use the provided `run.sh` script, which will:

1. Download ArXiv papers based on your search criteria.
2. Fetch references for the downloaded papers.
3. Download the referenced ArXiv papers (if available).

### Usage

First, make sure the `run.sh` script has execution permission:

```bash
chmod +x run.sh
```

Then, run the script with the following parameters:

```bash
./run.sh [KEYWORDS] [START_DATE] [END_DATE] [SAVE_DIR]
```

### Parameters:
- KEYWORDS: The keywords to search for in the paper titles and abstracts.
- START_DATE: The start date for the search in YYYYMMDD format.
- ND_DATE: The end date for the search in YYYYMMDD format.
- SAVE_DIR: The directory where papers and metadata will be saved.

### Example:
```bash
./run.sh "agent" "20240801" "20240911" "../../data/arxiv_ai_papers"
```
This will:
Download papers with the keyword "agent" submitted between 2024-08-01 and 2024-09-11.
Save the papers and metadata in the ../../data/arxiv_ai_papers directory.
Fetch references for the downloaded papers and save the updated metadata.

Output:
PDFs: Downloaded ArXiv papers in the specified directory.
paper_info.json: Metadata for the downloaded papers.
output_with_references.json: Metadata with references for each paper fetched via the Semantic Scholar API.
