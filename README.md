<div style="width: 100%;">
  <img src="assets/research_town.png" style="width: 100%;" alt="sotopia"></img>
</div>

<h1 align="center">Research Town: Simulator of Research Community</h1>

<div align="center">

[![Python 3.10](https://img.shields.io/badge/python-%E2%89%A53.10-blue)](https://www.python.org/downloads/release/python-3109/)
[![GitHub pull request](https://img.shields.io/badge/PRs-welcome-orange)](https://github.com/hiyouga/LLaMA-Factory/pulls)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![bear-ified](https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg)](https://beartype.readthedocs.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Github Action](https://github.com/ulab-uiuc/research-town/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/ulab-uiuc/research-town/actions/workflows/pytest.yml/badge.svg?branch=main)
[![Checked with mypy](https://github.com/ulab-uiuc/research-town/actions/workflows/mypy.yml/badge.svg?branch=main)](https://github.com/ulab-uiuc/research-town/actions/workflows/mypy.yml/badge.svg?branch=main)

[![Arxiv](https://img.shields.io/badge/arXiv-Coming%20soon-b31b1b)](https://github.com/ulab-uiuc/research-town)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/TwXxGhMB)
[![WeChat](https://img.shields.io/badge/WeChat-Join%20Us-09B83E?logo=wechat&logoColor=white)](assets/wechat.jpg)
[![codecov](https://codecov.io/github/ulab-uiuc/research-town/graph/badge.svg?token=00LRQFX0QR)](https://codecov.io/github/ulab-uiuc/research-town)

</div>

## Introduction

**Research Town** is a multi-agent platform designed for studying community-level automatic research. To achieve community-based simulation, it defines:

1. 🤖 *Researcher*: LLM research agents capable of skills such as reading papers, writing papers, discussing ideas, rebutting arguments, and writing reviews.
2. 🎩 *Environments*: Multi-agent environments, similar to virtual study rooms, where research agents collaborate on tasks like idea discussion, rebuttal writing, or paper writing.
3. ⚙️ *Engines*: Finite-state machines that manage agent involvement in environments and determine the next steps after task completion. For instance, engines guide agents coming out of idea discussion environment to paper writing environment and help select suitable agents to work together.


## Get started

### Install from pip

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

To run examples provided in the `examples`:

```bash
poetry install --extras "retriever collector logger"
```

To develop the UI part (both frontend and backend):

```bash
cd frontend
npm install
npm start
```

```bash
cd backend
uvicorn main:app --reload
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

## Developing

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


<p align="center">
<a href="https://star-history.com/#Significant-Gravitas/AutoGPT">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ulab-uiuc/research-town&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ulab-uiuc/research-town&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Significant-Gravitas/AutoGPT&type=Date" />
  </picture>
</a>
</p>
