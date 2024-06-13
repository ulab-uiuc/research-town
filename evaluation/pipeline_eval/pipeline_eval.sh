#!/bin/bash

# set args
domain_options=("natural_language_processing" "computer_vision" "graph_neural_networks" "federated_learning" "reinforcement_learning")
evaluator_model_options=("together_ai/meta-llama/Llama-3-70b-chat-hf" "together_ai/mistralai/Mixtral-8x22B-Instruct-v0.1" "gpt-4o")
agent_model_options=("llama3_70b" "mixtral_8_7b" "qwen_32" "llama3_8b")
eval_log_num=10

# 
for domain_option in "${domain_options[@]}"; do
    for evaluator_model_option in "${evaluator_model_options[@]}"; do
        for agent_model_option in "${agent_model_options[@]}"; do
            # print current option combination
            echo "Running with domain: $domain_option, evaluator model: $evaluator_model_option, agent model: $agent_model_option"
            # run
            python eval_pipeline.py --eval_log_num="$eval_log_num" --domain="$domain_option" --agent_model_name="$agent_model_option" --evaluator_model_name="$evaluator_model_option"
        done
    done
    # print domain completion message
    echo "Domain $domain_option completed."
done
