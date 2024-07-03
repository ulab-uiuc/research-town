<div style="width: 100%;">
  <img src="assets/research_town.png" style="width: 100%;" alt="sotopia"></img>
</div>

<h1 align="center">Research Town: Simulator of Human Research</h1>

<div align="center">
  <a href="https://www.python.org/downloads/release/python-3109/">
    <img src="https://img.shields.io/badge/python-3.10-blue.svg" alt="Python 3.10">
  </a>
  <a href="https://pre-commit.com/">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  </a>
  <a href="https://mypy-lang.org/">
    <img src="https://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy">
  </a>
  <a href="https://beartype.readthedocs.io">
    <img src="https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg" alt="bear-ified">
  </a>
  <a href="https://github.com/ulab-uiuc/research-town/actions/workflows/pytest.yml/badge.svg?branch=main">
    <img src="https://github.com/ulab-uiuc/research-town/actions/workflows/pytest.yml/badge.svg?branch=main" alt="Github Action">
  </a>
</div>

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

For some experiments, TogetherAI key is required to run the code. Please set the environment variable `TOGETHER_API_KEY` to your key. The recommend way is to add the key to the conda environment:

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

Run `pytest` to make sure all tests pass (this will ensure dynamic typing passed with beartype) and `mypy --strict .` to check static typing. (You can also run `pre-commit run --all-files` to run all checks)

#### Check github action result

Check the github action result to make sure all tests pass. If not, fix the errors and push again.
