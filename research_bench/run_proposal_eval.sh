#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./mlbench/mlbench.json"
OUTPUT_DIR="./results"
MODES=("citation_only" "author_citation" "zero_shot" "author_only")
NUM_PROCESSES=4

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    OUTPUT_PATH="${OUTPUT_DIR}/mlbench_result_4o_mini_${MODE}.jsonl"
    echo "Running evaluation for mode: $MODE"
    poetry run python run_proposal_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES"
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."
