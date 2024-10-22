#!/bin/bash

INPUT_PATH="./benchmark/crossbench.json"
MODE="citation_only"
OUTPUT_PATH="./results/crossbench_result_4o_mini_${MODE}.jsonl"

poetry run python run_evaluation.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE"
