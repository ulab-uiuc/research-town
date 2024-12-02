#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./paperbench/paper_bench_easy_500.json"
OUTPUT_DIR="./results"
MODES=("swarm") #("citation_only" "author_only" "author_citation" "sakana_ai_scientist")

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    OUTPUT_PATH="${OUTPUT_DIR}/mlbench_result_4o_mini_easy_${MODE}.jsonl"
    echo "Running evaluation for mode: $MODE"
    poetry run python run_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE"
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."
