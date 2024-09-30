#!/bin/bash

# -------------------------------------------------------------------
# run_create_bench.sh
# -------------------------------------------------------------------
# Description:
#   This script runs the create_bench.py Python script to generate
#   a benchmark dataset of AI-related arXiv papers based on specified
#   keywords and saves the output to a JSON file.
#
# Usage:
#   ./run_create_bench.sh
#
# -------------------------------------------------------------------

# Define the output path for the benchmark JSON file
OUTPUT_PATH="./benchmark/benchmark.json"

echo "Output will be saved to: $OUTPUT_PATH"

python3 create_bench.py --max_papers_per_keyword 10 --output "$OUTPUT_PATH"