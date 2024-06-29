# ResearchEval

We built ResearchEval based on ResearchTown in the current version. In future versions, we will separate them.

## Important Components of ResearchEval

ResearchEval consists of three important parts:

1. **Prompting-based Evaluators**: See `research_town/evaluators`.
2. **Evaluation Prompt Templates**: See `research_town/utils/eval_prompter.py`.
3. **Evaluation Experiments**: Includes scripts for pipeline and held-out evaluations—see `evaluations/`, and evaluation data for inputs and outputs in `data/eval_data`.

## Evaluation Preparation

You can view an episode evaluation with default parameters by following the instructions below.

### Step 1. Install the `research_town` Package

```bash
pip install poetry
poetry lock --no-update
poetry install
```

### Step 2. Export Your API Keys

We adopt LiteLLM as our API router. See details [here](https://docs.litellm.ai/docs/providers). An example of applying the OpenAI API key is:

```bash
export OPENAI_API_KEY=YOUR_API_KEY
```

### Step 3. Run the Scripts

#### Evaluation Demo

To point out, the following script is just a minimal demo that only supports the TogetherAI API key.

```bash
export TOGETHERAI_API_KEY=YOUR_API_KEY
python examples/evaluate_log.py
```

#### (Recommended) Detailed Evaluations

For more detailed evaluations with different models, you can run with model providers supported by LiteLLM. We recommend [TogetherAI](https://docs.litellm.ai/docs/providers/togetherai) and [OpenAI](https://docs.litellm.ai/docs/providers/openai), as all evaluators in our scripts are from these two providers.

```bash
export TOGETHERAI_API_KEY=YOUR_API_KEY
export OPENAI_API_KEY=YOUR_API_KEY
```

After you set the API key, you could run the experiments for **held-out** & **pipeline evaluations** mentioned in our paper. Detailed instructions are in two other `readme.md` files as follows.

- **Held-out Evaluation Scripts**: See `evaluation/heldout_eval/readme.md`.
- **Pipeline Evaluation Scripts**: See `evaluation/pipeline_eval/readme.md`.