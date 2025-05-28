#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./paperbench/camera-ready/paper_bench_full_1000_filtered_1205.json"  # Updated input path for deeoseek v3
OUTPUT_DIR="./results"
MODES=("zero_shot" "author_only" "citation_only") # "author_citation") # 

NUM_PROCESSES=4

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    OUTPUT_PATH="${OUTPUT_DIR}/paperbench_result_deepseek_v3_${MODE}_1000_full.jsonl"
    echo "Running evaluation for mode: $MODE"
    poetry run python run_proposal_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES" --config_path "../configs_deepseek_v3"  # Added config_path for deeoseek v3
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."
