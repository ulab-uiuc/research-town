# research-town

## Demo

You can view an episode demo with default parameters by running:

Step1. Install research_town package that we wrote.

```bash
poetry install
```

Step2. Run the scripts

```bash
python examples/minimal_demo.py
```
## Microbench

You can run the microbench of review process by running:

Step1. Install research_town package that we wrote.

```bash
poetry install
```

Step2. Run the scripts

Next, run the script microbench_review.py with the desired arguments:

```bash
python examples/microbench_review.py --review_agent_num=3  --model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'
```

#### Explanation of Arguments
1. --data_path: Specifies the path to the data directory for the microbenchmark. If not provided, it defaults to a predefined path within the script.
Example: --data_path="/path/to/data"
2. --domain: Specifies the domain of papers to be reviewed. The default is "machine_learning_system".
Example: --domain="machine_learning_system"
3. --model_name: Specifies the model to be used for reviewers. The default model is 'together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1'.
Example: --model_name="gpt-4o"
4. --review_agent_num: Specifies the total number of research agents (reviewers). The default is 3.
Example: --review_agent_num=1
