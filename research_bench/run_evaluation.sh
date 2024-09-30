#!/bin/bash

INPUT="./data/arxiv_ai_papers/test_paper.json"
OUTPUT="./results/test_results.jsonl"

poetry run python run_evaluation.py --input "$INPUT" --output "$OUTPUT"