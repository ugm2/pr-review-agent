#!/bin/bash
# PR Review Agent wrapper script
# Usage: pr-review.sh [options]
# Run from any Git repository to analyze changes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALLER_DIR="$(pwd)"
export PYTHONPATH="$SCRIPT_DIR/src"

cd "$CALLER_DIR"
uv run --project "$SCRIPT_DIR" python -m pr_review_agent.cli "$@"
