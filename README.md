# ResearchEval
We built the ResearchEval based on ResearchTown in the current version. In the future version, we will separate them.

## Important Component of ResearchEval
ResearchEval consists of three important parts:
(1) Prompting-based evaluators: see research_town/evaluators.
(2) Evaluation prompt templates: see research_town/utils/eval_prompter.py.
(3) Evaluation experiments: include scripts for pipeline and held-out evaluations--- see evaluations/, and evaluation data for inputs and outputs in data/eval_data.

## Evaluation preperation

You can view an episode evaluation with default parameters by running instructions as follows.

### Step 1. Install research_town package that we wrote.

```bash
poetry install
```

### Step 2. Export your API keys. 
We adopt litellm as our API router. See details [here](https://docs.litellm.ai/docs/providers). An example of applying OpenAI API key is:

```bash
export OPENAI_API_KEY=YOUR_API_KEY
```

### Step 3. Run the scripts as follows.


#### Evaluation Demo
To point out, the following script is just a minimal demo that only supports the TogetehrAI API key.

```bash
export export TOGETHERAI_API_KEY=YOUR_API_KEY
python examples/evaluate_log.py
```

#### (Recommended) Detailed Evaluations
 More detailed evaluations with different models are here. You can run with model providers supported by litellm [here](https://docs.litellm.ai/docs/providers). We recommend [TogetherAI](https://docs.litellm.ai/docs/providers/togetherai) and [OpenAI](https://docs.litellm.ai/docs/providers/openai) as all evaluators in our scripts are from these two providers.

 ```bash
export TOGETHERAI_API_KEY=YOUR_API_KEY
export OPENAI_API_KEY=YOUR_API_KEY=YOUR_API_KEY
```

How to run held-out evaluation scripts? See evaluation/heldout_eval/readme.md.

How to run pipeline evaluation scripts? See evaluation/pipleline_eval/readme.md.