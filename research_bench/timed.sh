#!/bin/bash

# Wait for 1.5 hours

# sleep 5400  # 1.5 hours = 5400 seconds
# wait with a countdown

secs=$((1*25*60))
while [ $secs -gt 0 ]; do
   echo -ne "Waiting for 25 minutes to finish. Time left: $secs\033[0K\r"
   sleep 1
   : $((secs--))
done

echo "Finished waiting for 1.5 hours."

# Copy the file
cp results/iclrbench_result_4o_mini_research_town_topk_3.jsonl iclrbench/review_evaluation/iclrbench_result_4o_mini_research_town_topk_3.jsonl

# Change directory to review_evaluation
cd iclrbench/review_evaluation

# Run the evaluation script
bash auto_eval.sh

echo "Finished running the evaluation script."
