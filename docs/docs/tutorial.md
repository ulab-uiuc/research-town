---
sidebar_position: 2
---

# Tutorial

## Get started

### Install from package

You can install `research_town` from `pypi` to use it as a package:

```bash
pip install research_town
```

### Install from scratch

Use a virtual environment, e.g. with anaconda3:

```bash
conda create -n research_town python=3.10
conda activate research_town
curl -sSL https://install.python-poetry.org | python3
```

Then, install the requirements and this package with one command line:

```bash
poetry install
```

### Configure API keys

OpenAI key is required to run the code. Please set the environment variable `OPENAI_API_KEY` to your key. The recommend way is to add the key to the conda environment:

```
conda env config vars set OPENAI_API_KEY=your_key
```

For some experiments, TogetherAI key is required to run the code. Please set the environment variable `TOGETHERAI_API_KEY` to your key (notice: not `TOGETHER_API_KEY`). The recommend way is to add the key to the conda environment:

```
conda env config vars set TOGETHER_API_KEY=your_key
```
