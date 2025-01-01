#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./reviewbench/reviewbench_reviewers_full_content.json"
OUTPUT_DIR="./results"
MODES=("research_town")
NUM_PROCESSES=4
TOP_K_REVIEWERS=5

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    OUTPUT_PATH="${OUTPUT_DIR}/reviewbench_result_4o_mini_${MODE}_top${TOP_K_REVIEWERS}.json"
    echo "Running evaluation for mode: $MODE"
    poetry run python run_review_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES" --top_k_reviewers "$TOP_K_REVIEWERS"
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."
