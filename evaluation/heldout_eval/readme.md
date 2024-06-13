# Held-out Evaluation

This is a unit evaluation focused on collecting papers from OpenReview for ICLR'23 across 5 domains.

## Run Scripts

### Review Score

```bash
python evaluation/heldout_eval/review_score_eval/eval_review_score.py --review_agent_num=3 --review_paper_num=20 --model_name="gpt-4o" --domain='computer_vision'
```

### Review Content

```bash
python evaluation/heldout_eval/review_content_eval/eval_review_content.py --model_name="gpt-4o" --review_paper_num=10 --domain='computer_vision'
```

### Arguments

1. `--domain`: Specifies the domain of the paper. Options include:
   - "natural_language_processing"
   - "computer_vision"
   - "graph_neural_networks"
   - "federated_learning"
   - "reinforcement_learning"

2. `--model_name`: Specifies the model to use. Ensure that the model name aligns with your model provider's conventions. Examples of OpenAI and TogetherAI models include:
   - `--model_name="gpt-4o"`
   - `--model_name="together_ai/meta-llama/Llama-3-70b-chat-hf"`
3. `--review_paper_num`: how many papers with reviews to evaluate. 
4. `--review_agent_num`: for each paper, the number of agents as its reviewers. 



