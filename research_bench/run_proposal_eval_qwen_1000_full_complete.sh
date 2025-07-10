#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./paperbench/camera-ready/paper_bench_full_1000_filtered_1205.json"  # Updated input path for deeoseek v3
OUTPUT_DIR="./results"
MODES=("citation_only" "author_citation" "zero_shot" "author_only") #
NUM_PROCESSES=4

# Define a function to run the evaluation
run_eval() {
    local MODE=$1
    OUTPUT_PATH="${OUTPUT_DIR}/paperbench_result_qwen_${MODE}_1000_full_4096_delete_incomplete.jsonl"
    echo "Running evaluation for mode: $MODE"
    poetry run python run_proposal_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes 1 --config_path "../configs_qwen_8192"
    echo "Finished evaluation for mode: $MODE"
}

# Export variables and functions needed for parallel execution
export OUTPUT_DIR INPUT_PATH
export -f run_eval

# Run in parallel using xargs
printf "%s\n" "${MODES[@]}" | xargs -P ${NUM_PROCESSES:-4} -I {} bash -c 'run_eval "$@"' _ {}

echo "All modes tested successfully."
