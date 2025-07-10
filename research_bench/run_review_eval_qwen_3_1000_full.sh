# #!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./iclrbench/camera-ready/review_bench.json"
OUTPUT_DIR="./results"
MODES=("reviewer_only")  # Added more modes for testing
export DATABASE_FOLDER_PATH="."
NUM_PROCESSES=4

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    # OUTPUT_PATH="${OUTPUT_DIR}/iclrbench_result_qwen_${MODE}_200_full.jsonl" top_k 1
    OUTPUT_PATH="${OUTPUT_DIR}/iclrbench_result_qwen_${MODE}_200_full_topk_5.jsonl"
    echo "Running evaluation for mode: $MODE"
    CUDA_VISIBLE_DEVICES=9 poetry run python run_review_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES" --config_path ../configs_qwen_1024
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."
