#!/bin/bash

# Variables for downloading arXiv papers
KEYWORDS="agent"
START_DATE="20240915"
END_DATE="20240925"
SAVE_DIR="./data/arxiv_ai_papers"

# Step 1: Download arXiv papers
python3 download_arxiv_papers.py --keywords $KEYWORDS --start_date $START_DATE --end_date $END_DATE --save_dir $SAVE_DIR

# Step 2: Fetch references for downloaded papers
INPUT_FILE="$SAVE_DIR/paper_info.json"
OUTPUT_FILE="$SAVE_DIR/output_with_references.json"

python3 get_reference_papers.py --input_file $INPUT_FILE --output_file $OUTPUT_FILE

# Step 3: Download the references' PDFs
python3 download_reference_papers.py --input_file "$OUTPUT_FILE" --output_file "$SAVE_DIR/output_with_downloaded_references.json" --save_dir "$SAVE_DIR"
