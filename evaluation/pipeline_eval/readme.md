# Review Evaluation

This is a pipeline evaluation of idea/paper/review generated in research town across 5 domains.

## Run Scripts for all evaluation settings

```bash
cd evaluation/pipeline_eval/
bash pipeline_eval.sh
```
to parse output（make sure you get output for all settings）, you could run:
```bash
python evaluation/pipeline_eval/parse_pipeline_eval_output.py
```
### Pipeline evaluation for single setting
If you want to conduct pipeline evaluation for a single setting, you could run like:

```bash
python evaluation/pipeline_eval/eval_pipeline.py  --eval_log_num=10 --domain='computer_vision' --agent_model_name="llama3_70b" --evaluator_model_name="gpt-4o"
```



### Arguments

1. `--domain`: Specifies the domain of the paper. Options include:
   - "natural_language_processing"
   - "computer_vision"
   - "graph_neural_networks"
   - "federated_learning"
   - "reinforcement_learning"

2. `--evaluator_model_name`: Specifies the evaluator model to use. Ensure that the model name aligns with your model provider's conventions. 

   Examples of TogetherAI models include:
   - `--evaluator_model_name="together_ai/meta-llama/Llama-3-70b-chat-hf"`
   - `--evaluator_model_name="together_ai/mistralai/Mixtral-8x22B-Instruct-v0.1"`

   Examples of OpenAI models include:
   - `--evaluator_model_name="gpt-4o"`
3. `--eval_log_num`: how many logs of idea/paper/ review to evaluate. 
4. `--agent_model_name`: means which model works as agents that the logs are collected from.  choices=['llama3_70b', 'mixtral_8_7b','qwen_32','llama3_8b']


