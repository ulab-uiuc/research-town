# attackprompt
# poetry run python run_attack.py \
#     --adversarial_path './attackbench/adversarial.json' \
#     --profile_path './attackbench/profiles.json' \
#     --output_path './attackbench/attack_results.jsonl' 
#     --num_processes 5 \ 

# original_task: The task to attack
# poetry run python run_attack.py \
#     --adversarial_path './attackbench/adversarial.json' \
#     --profile_path './attackbench/profiles.json' \
#     --output_path './attackbench/attack_results_origin.jsonl' \
#     --original_task \
#     --num_workers 5

# attacker agent
# poetry run python run_attack.py \
#     --adversarial_path './attackbench/adversarial.json' \
#     --profile_path './attackbench/contaminated_profiles.json' \
#     --output_path './attackbench/attack_results_attacker_agent.jsonl' \
#     --original_task \
#     --num_workers 5

# attacker agent with attack prompt
# poetry run python run_attack.py \
#     --adversarial_path './attackbench/adversarial.json' \
#     --profile_path './attackbench/contaminated_profiles.json' \
#     --output_path './attackbench/attack_results_attacker_agent_attack_prompt.jsonl' \
#     --num_workers 5

# ethical review process with original task
# poetry run python run_attack.py \
#     --adversarial_path './attackbench/adversarial.json' \
#     --profile_path './attackbench/profiles.json' \
#     --output_path './attackbench/ethical_result_original_task.jsonl' \
#     --original_task \
#     --num_workers 5 \
#     --ethical_review

# ethical review process with attacker agent in original task
# poetry run python run_attack.py \
#     --adversarial_path './attackbench/adversarial.json' \
#     --profile_path './attackbench/contaminated_profiles.json' \
#     --output_path './attackbench/ethical_result_attacker_agent.jsonl' \
#     --original_task \
#     --num_workers 5 \
#     --ethical_review

# defense agent with original task
# poetry run python run_attack.py \
#     --adversarial_path './attackbench/adversarial.json' \
#     --profile_path './attackbench/profiles_ethical.json' \
#     --output_path './attackbench/defense_agent_result_original_task.jsonl' \
#     --original_task \
#     --num_workers 5 \

# defense agent with attacker agent in original task
poetry run python run_attack.py \
    --adversarial_path './attackbench/adversarial.json' \
    --profile_path './attackbench/profiles_malicious_ethical.json' \
    --output_path './attackbench/defense_agent_result_attacker_agent.jsonl' \
    --original_task \
    --num_workers 5 \

