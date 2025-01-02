<div style="width: 100%;">
  <img src="assets/research_town.png" style="width: 100%;"></img>
</div>

<h1 align="center">ResearchTown: Simulator of Human Research Community</h1>

<div align="center">

[![Python 3.10](https://img.shields.io/badge/python-%E2%89%A53.10-blue)](https://www.python.org/downloads/release/python-3109/)
[![Dataset](https://img.shields.io/badge/%F0%9F%A4%97-ResearchBench-yellow)](https://huggingface.co/datasets/ulab-ai/research-bench)
[![Arxiv](https://img.shields.io/badge/arXiv-ResearchTown-b31b1b)](https://arxiv.org/pdf/2412.17767)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/9t9jtDDk)
[![WeChat](https://img.shields.io/badge/WeChat-Join%20Us-09B83E?logo=wechat&logoColor=white)](assets/wechat.png)
[![codecov](https://codecov.io/github/ulab-uiuc/research-town/graph/badge.svg?token=00LRQFX0QR)](https://codecov.io/github/ulab-uiuc/research-town)


[English](README.md) | [中文](README-CN.md)
</div>

## News
* [12/24] We release our ResearchTown paper on [arXiv](https://arxiv.org/pdf/2412.17767) and ResearchBench data on [HuggingFace](https://huggingface.co/datasets/ulab-ai/research-bench).

## Introduction

**Research Town** is a multi-agent platform designed for studying community-level automatic research. To achieve community-based simulation, it defines:

1. 🤖 *Researcher*: LLM research agents capable of skills such as reading papers, writing papers, discussing ideas, rebutting arguments, and writing reviews.
2. 🎩 *Environments*: Multi-agent environments, similar to virtual study rooms, where research agents collaborate on tasks like idea discussion, rebuttal writing, or paper writing.
3. ⚙️ *Engines*: Finite-state machines that manage agent involvement in environments and determine the next steps after task completion. For instance, engines guide agents coming out of idea discussion environment to paper writing environment and help select suitable agents to work together.


## Get started

### Install from pip

You can install `research-town` from `pypi` to use it as a package:

```bash
pip install research-town
```

### Install from scratch

Use a virtual environment, e.g. with anaconda3:

```bash
conda create -n research-town python=3.10
conda activate research-town
curl -sSL https://install.python-poetry.org | python3
export PATH="$HOME/.local/bin:$PATH"
```

### Configure environment variables
Environment variables such as `OPENAI_API_KEY` and database related configs are required to run the code. The recommended way to set all the required variable is
1. Copy the `.env.template` file into the project root with the name `.env`.
```bash
cp .env.template .env
```
2. Fill the required environment variables in the `.env` file.

### Running the examples
To run examples provided in the `examples`:

```bash
poetry install
cd examples
python research_town_demo.py
```

All generated research progress like ideas, proposals will be automatically saved in the database folder you set in the .env file.

## Developing

#### Develop Demo

To develop the demo (both frontend and backend):
Set `DATABASE_FOLDER_PATH=./sample_data` in .env file
```bash
cd frontend
npm install
npm start
```

```bash
poetry install -E backend
uvicorn backend.app.main:app --reload
```

#### Install dev options

Follow the installation instruction above and then, instead of running `python -m pip install -e .`, run the following commands:

```
python -m pip install -e ".[dev]"
mypy --install-types --non-interactive research_town
python -m pip install pre-commit
pre-commit install
```

The installation of pre-commit would avoid formatting error and large file injects into github commits.

#### New branch for each feature

`git checkout -b feature/feature-name` and PR to `main` branch.

#### Before committing

Run `poetry run pytest` to make sure all tests pass (this will ensure dynamic typing passed with beartype) and `poetry run mypy --config-file pyproject.toml .` to check static typing. (You can also run `pre-commit run --all-files` to run all checks)

#### Check github action result

Check the github action result to make sure all tests pass. If not, fix the errors and push again.


## ResearchBench

To execute ResearchBench experiments, please execute 'research_bench/run_review_eval.sh' script. You can adjust the parameters in the script, using the actual `INPUT_PATH`.

If you encounter `openreview` not found error, please install the package by running `pip install openreview`. If any issues come up regarding `requests`, please change its version to `2.26`.

```bash
pip install requests==2.26
```
