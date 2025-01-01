<div style="width: 100%;">
  <img src="assets/research_town.png" style="width: 100%;"></img>
</div>

<h1 align="center">Research Town: Simulator of Research Community </h1>

<div align="center">

[![Python 3.10](https://img.shields.io/badge/python-%E2%89%A53.10-blue)](https://www.python.org/downloads/release/python-3109/)
[![GitHub pull request](https://img.shields.io/badge/PRs-welcome-orange)](https://github.com/hiyouga/LLaMA-Factory/pulls)
[![Arxiv](https://img.shields.io/badge/arXiv-Coming%20soon-b31b1b)](https://github.com/ulab-uiuc/research-town)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/TwXxGhMB)
[![WeChat](https://img.shields.io/badge/WeChat-Join%20Us-09B83E?logo=wechat&logoColor=white)](assets/wechat.png)
[![codecov](https://codecov.io/github/ulab-uiuc/research-town/graph/badge.svg?token=00LRQFX0QR)](https://codecov.io/github/ulab-uiuc/research-town)


[English](README.md) | [中文](README-CN.md)
</div>

## 简介

**Research Town** 是一个多智能体平台并实现基于社区环境的模拟，并定义了以下内容：

1. 🤖 *撰写者*：智能体具备阅读、撰写论文，讨论、反驳以及撰写评审的能力。
2. 🎩 *环境*：多智能体环境模拟虚拟的学习室，协作完成任务，讨论想法、撰写反驳并完成论文。
3. ⚙️ *驱动引擎*：我们定义了有限状态机(Finite-state Machines)，管理智能体在不同环境中的参与情况，决定任务完成后的下一步操作。引导智能体从想法讨论环境一步一步论文撰写环境，并帮助选择合适的智能体协作完成任务。

## 快速开始

### 使用 pip 安装

通过 `pypi` 安装 `research-town` ：

```bash
pip install research-town
```

### 虚拟环境安装

```bash
conda create -n research-town python=3.10
conda activate research-town
curl -sSL https://install.python-poetry.org | python3
```

### 配置环境变量

例如 `OPENAI_API_KEY` 和与数据库相关的配置。推荐的设置方法如下：

1. 将 `.env.template` 文件复制到项目根目录，并命名为 `.env`。
```bash
cp .env.template .env
```
2. 在 `.env` 文件中填写所需的环境变量。

### 运行示例

运行 `examples` 中提供的示例：

```bash
poetry install
cd examples
python research_town_demo.py
```

## 开发

### Demo

开发 Demo（包括前端和后端）：
设置 `DATABASE_FOLDER_PATH=./sample_data` 在 .env 文件中，然后运行：

```bash
cd frontend
npm install
npm start
```

```bash
poetry install -E backend
uvicorn backend.app.main:app --reload
```

### 安装开发选项

按照上面的安装步骤，然后执行以下命令代替运行 python -m pip install -e .：

```
python -m pip install -e ".[dev]"
mypy --install-types --non-interactive research_town
python -m pip install pre-commit
pre-commit install
```
安装 pre-commit 可避免代码格式错误和大文件被提交到 GitHub。

#### 为每个功能创建新分支

使用 `git checkout -b feature/feature-name` 创建新分支，并向 main 分支提交 修改。

#### 提交前检查

运行 poetry run pytest 确保所有测试通过（这将确保通过动态类型检查 beartype），并运行 poetry run mypy --config-file pyproject.toml . 检查静态类型。（您也可以运行 pre-commit run --all-files 来运行所有检查）

#### 检查 GitHub Actions 结果

检查 GitHub Actions 的结果，确保所有测试通过。若未通过，请修复错误并重新提交。

<p align="center">
<a href="https://star-history.com/#Significant-Gravitas/AutoGPT">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ulab-uiuc/research-town&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ulab-uiuc/research-town&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Significant-Gravitas/AutoGPT&type=Date" />
  </picture>
</a>
</p>

## ResearchBench

要执行ResearchBench实验，请运行 'research_bench/run_review_eval.sh' 脚本。你可以在脚本中调整参数，如使用实际的 `INPUT_PATH`。

如果遇到 `openreview` 未找到的错误，请通过运行 `pip install openreview` 安装该包。如果遇到与 `requests` 相关的问题，请将其版本更改为 `2.26`。

```bash
pip install requests==2.26
```