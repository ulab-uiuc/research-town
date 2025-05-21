#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./paperbench/paper_bench_hard_500_filtered_1205_extended_with_reviewers.json"
OUTPUT_DIR="./results"
MODES=("zero_shot" "author_only" "citation_only" "author_citation")
NUM_PROCESSES=4

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    OUTPUT_PATH="${OUTPUT_DIR}/paperbench_gnn_v2_result_4o_mini_${MODE}.jsonl"
    echo "Running evaluation for mode: $MODE"
    poetry run python run_proposal_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES"
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."

#!/bin/bash

# # Define the input and output paths, along with the modes to test
# INPUT_PATH="./paperbench/paper_bench_hard_500_filtered_1205_extended_with_reviewers.json"
# OUTPUT_DIR="./results"
# MODES=("zero_shot" "author_only" "citation_only" "author_citation")
# NUM_PROCESSES=4

# # Loop through each mode and run the evaluation in the background
# for MODE in "${MODES[@]}"
# do
#     OUTPUT_PATH="${OUTPUT_DIR}/paperbench_gnn_v2_result_4o_mini_${MODE}.jsonl"
#     echo "Running evaluation for mode: $MODE"
#     CUDA_VISIBLE_DEVICES=1 poetry run python run_proposal_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES" &
# done

# # Wait for all background jobs to finish
# wait

# echo "All modes tested successfully."
