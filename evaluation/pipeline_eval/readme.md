# Review Evaluation

This is a pipeline evaluation of idea/paper/review generated in research town across 5 domains.

## Run Scripts



### Pipeline evaluation

```bash
python evaluation/pipeline_eval/eval_pipeline.py --evaluator_model_name="together_ai/meta-llama/Llama-3-70b-chat-hf" --eval_log_num=10 --domain='computer_vision' --agent_model_name="LLaMA-3_70"
```

## Arguments

1. `--domain`: Specifies the domain of the paper. Options include:
   - "natural_language_processing"
   - "computer_vision"
   - "graph_neural_networks"
   - "federated_learning"
   - "reinforcement_learning"

2. `--evaluator_model_name`: Specifies the evaluator model to use. Ensure that the model name aligns with your model provider's conventions. Examples of TogetherAI models include:
   - `--model_name="together_ai/Qwen/Qwen1.5-110B-Chat"`
   - `--model_name="together_ai/meta-llama/Llama-3-70b-chat-hf"`
3. `--eval_log_num`: how many logs of idea/paper/ review to evaluate. 
4. `--agent_model_name`: means which model works as agent that the logs are collected from.  choices=['LLaMA-3_70', 'Mixtral_8_7B','LLaMA-3_8','QWen_1.5_32']



