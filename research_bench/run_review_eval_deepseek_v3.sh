# #!/bin/bash

# # Define the input and output paths, along with the modes to test
# INPUT_PATH="./iclrbench/iclrbench_reviewers_filtered_bullets.json"
# OUTPUT_DIR="./results"
# MODES=("research_town")
# NUM_PROCESSES=4

# # Loop through each mode and run the evaluation
# for MODE in "${MODES[@]}"
# do
#     OUTPUT_PATH="${OUTPUT_DIR}/iclrbench_result_deepseek_v3_${MODE}_topk_1.jsonl"
#     echo "Running evaluation for mode: $MODE"
#     CUDA_VISIBLE_DEVICES=9 poetry run python run_review_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES" --config_path ../configs_deepseek_v3
#     echo "Finished evaluation for mode: $MODE"
# done

# echo "All modes tested successfully."

#!/bin/bash

# Define the input and output paths, along with the modes to test
INPUT_PATH="./iclrbench/iclrbench_reviewers_filtered_bullets_8.json"
OUTPUT_DIR="./results"
MODES=("research_town")  # Added more modes for testing
NUM_PROCESSES=4

# Loop through each mode and run the evaluation
for MODE in "${MODES[@]}"
do
    OUTPUT_PATH="${OUTPUT_DIR}/iclrbench_result_deepseek_v3_${MODE}.jsonl"
    echo "Running evaluation for mode: $MODE"
    CUDA_VISIBLE_DEVICES=9 poetry run python run_review_eval.py --input "$INPUT_PATH" --output "$OUTPUT_PATH" --mode "$MODE" --num_processes "$NUM_PROCESSES" --config_path ../configs_deepseek_v3
    echo "Finished evaluation for mode: $MODE"
done

echo "All modes tested successfully."
