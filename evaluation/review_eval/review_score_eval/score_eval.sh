#!/bin/bash


review_agent_num=3
review_paper_num=20


model_names=("together_ai/meta-llama/Llama-3-70b-chat-hf") # model_names=("gpt-4o" "together_ai/meta-llama/Llama-3-70b-chat-hf")


domain_options=("natural_language_processing" "computer_vision" "graph_neural_networks" "federated_learning" "reinforcement_learning")


for model_name in "${model_names[@]}"; do
  echo "Starting evaluations for model: $model_name"
  for domain in "${domain_options[@]}"; do
    args="--review_agent_num=$review_agent_num --review_paper_num=$review_paper_num --model_name=\"$model_name\" --domain=\"$domain\""
    echo "Running with args: $args"
    # run pythono script
    python eval_review_score.py \
      --review_agent_num=$review_agent_num \
      --review_paper_num=$review_paper_num \
      --model_name="$model_name" \
      --domain="$domain"
  done
  echo "Completed evaluations for model: $model_name"
done
