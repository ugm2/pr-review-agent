# PR Review Agent

An agentic system that performs PR reviews from local `git diff` using Groq for SOTA LLM inference.

## Features
- **LangGraph Orchestration**: Robust state management and workflow control using LangGraph.
- **Observability**: Complete tracing and monitoring with LangSmith.
- **ReAct Loop**: Plans and runs tools (pytest, ruff, mypy, ripgrep) before reviewing.
- **Grounded Feedback**: Comments are backed by tool evidence.
- **SOTA Models**: Optimized for `llama-3.3-70b-versatile` on Groq.
- **JSON & Markdown**: Supports structured output for automation or human-readable formats.

## Installation

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended)
- A Groq API Key

### Setup
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd pr-review-agent
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Configure your API key:
   Set the `GROQ_API_KEY` in your environment or a `.env` file:
   ```bash
   export GROQ_API_KEY="your_api_key_here"
   ```


## Observability (LangSmith)

This agent supports comprehensive tracing via [LangSmith](https://smith.langchain.com/). 
See [LANGSMITH_SETUP.md](LANGSMITH_SETUP.md) for detailed setup instructions.

## Usage

The PR review agent analyzes Git diffs in any repository. You can run it from any Git repository directory.

### Run a Review

Review your **staged** changes:
```bash
~/Desktop/Developer/pr-review-agent/pr-review.sh
```

Review **unstaged** changes (modified but not staged):
```bash
~/Desktop/Developer/pr-review-agent/pr-review.sh --mode unstaged
```

Review **all uncommitted** changes (staged + unstaged):
```bash
~/Desktop/Developer/pr-review-agent/pr-review.sh --mode working-tree
```

Review a specific **branch**:
```bash
~/Desktop/Developer/pr-review-agent/pr-review.sh --mode branch --base-ref main
```

Review a **commit range**:
```bash
~/Desktop/Developer/pr-review-agent/pr-review.sh --mode commit-range --base-ref origin/main --head-ref HEAD
```

### Create a Shell Alias (Recommended)

For easier access from any repository, add this to your `~/.zshrc` or `~/.bashrc`:
```bash
alias pr-review="~/Desktop/Developer/pr-review-agent/pr-review.sh"
```

Then reload your shell:
```bash
source ~/.zshrc
```

Now you can simply run:
```bash
cd /path/to/any/repository
pr-review --mode branch --base-ref main
```

### Options
- `--repo-root`: Root directory of the repository (default: current directory).
- `--mode`: Diff mode (default: `staged`):
  - `staged`: Only staged changes
  - `unstaged`: Only unstaged changes (modified but not staged)
  - `working-tree`: All uncommitted changes (staged + unstaged)
  - `branch`: Changes compared to a branch
  - `commit-range`: Changes between two commits
- `--base-ref`: Base reference for diff (required for `branch` and `commit-range` modes).
- `--head-ref`: Head reference for diff (for `commit-range` mode).
- `--format`: `markdown` (default) or `json`.
- `--model`: Change the Groq model (default: `llama-3.3-70b-versatile`).
- `--max-iters`: Limit the number of ReAct tools iterations (default: 3).

## Development
To run tests (after implementing them in `tests/`):
```bash
uv run pytest
```

