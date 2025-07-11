# ResearchEval

We built ResearchEval based on ResearchTown in the current version. In future versions, we will separate them.

## Important Components of ResearchEval

ResearchEval consists of two important parts:

1. **Prompting-based Evaluations**:
   1. **Prompting-based Evaluators**: See `research_town/evaluators`.
   2. **Evaluation Prompt Templates**: See `research_town/utils/eval_prompter.py`.
   3. **Evaluation Examples**: See `examples/research_eval_demo.py` for pipeline evaluations.
2. **Human-based Evaluations**: Includes scripts of human evaluation analysis—see `human_eval/`.

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

For more detailed evaluations with different models, you can run with model providers supported by LiteLLM. We recommend [TogetherAI](https://docs.litellm.ai/docs/providers/togetherai) and [OpenAI](https://docs.litellm.ai/docs/providers/openai), as all evaluators in our scripts are from these two providers.

```bash
export TOGETHERAI_API_KEY=YOUR_API_KEY
export OPENAI_API_KEY=YOUR_API_KEY
```

### Step 3. Run the Scripts

#### Pipeline Evaluation Demo

To run the demo for prompting-based pipeline evaluation of the entire research progress, run:

```bash
python examples/research_eval_demo.py
```

#### Human Evaluation Analysis

We place the demo for human evaluation analysis in `scripts/human_eval`.

```bash
export TOGETHERAI_API_KEY=YOUR_API_KEY
python scripts/human_eval/human_eval_analysis.py
```
