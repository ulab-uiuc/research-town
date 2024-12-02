#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./paper_bench/paper_bench_hard_500.json"
OUTPUT_DIR="./results"
MODES=("citation_only")
NUM_PROCESSES=1

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    OUTPUT_PATH="${OUTPUT_DIR}/paper_bench_hard_500_result_4o_mini_${MODE}.jsonl"
    echo "Running evaluation for mode: $MODE"
    poetry run python run_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES"
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."
