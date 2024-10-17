#!/bin/bash

# Define input and output file paths
INPUT="./benchmark/mlbench.json"
OUTPUT="./results/research_bench_result_4o_mini_single_agent.jsonl"
INTRO_LOG="./benchmark/intro_logging.jsonl"
TEST_SINGLE_AGENT="--test-single-agent"
TOTAL_LINES=100

# Function to get the number of lines in the output file
get_line_count() {
  wc -l < "$OUTPUT"
}

# Ensure the output directory exists
OUTPUT_DIR=$(dirname "$OUTPUT")
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "Output directory does not exist. Creating: $OUTPUT_DIR"
  mkdir -p "$OUTPUT_DIR"
fi

# Check if the output file exists; if not, create it
if [ ! -f "$OUTPUT" ]; then
  echo "Output file does not exist. Creating: $OUTPUT"
  touch "$OUTPUT"
else
  echo "Output file exists: $OUTPUT"
fi

# Get the current number of lines in the output file
current_lines=$(get_line_count)
echo "Current line count in output file: $current_lines"

# Loop until the output file has at least 100 lines
while [ "$current_lines" -lt 100 ]; do
  echo "Line count is less than 100. Running the evaluation script..."

  # Run the evaluation script
  poetry run python run_evaluation.py --input "$INPUT" --output "$OUTPUT" --intro_log "$INTRO_LOG" $TEST_SINGLE_AGENT

  # Update the current line count
  current_lines=$(get_line_count)
  echo "Updated line count in output file: $current_lines"

  # If still less than 100 lines, wait for 3 seconds before retrying
  if [ "$current_lines" -lt 100 ]; then
    echo "Line count still less than 100. Waiting for 3 seconds before retrying..."
    sleep 3
  fi
done

echo "Output file has reached or exceeded 100 lines. Script completed."
