# LangSmith Setup Guide

[LangSmith](https://smith.langchain.com/) is a platform for debugging, testing, and monitoring LLM applications. This agent integrates with LangSmith to provide detailed traces of every PR review.

## 1. Sign Up
1. Go to [smith.langchain.com](https://smith.langchain.com/) and sign up (free tier available).
2. Create an organization if prompted.

## 2. Get API Key
1. Navigate to **Settings** (gear icon) on the bottom left.
2. Go to the **API Keys** tab.
3. Click **Create API Key**.
4. Copy the key (it starts with `lsv2_...`).

## 3. Configuration

### Environment Variables
Add the following to your `.env` file:

```bash
# Required for tracing
LANGSMITH_API_KEY="<your-api-key>"

# Optional configuration
LANGSMITH_PROJECT="pr-review-agent"  # Groups traces under this project
LANGSMITH_TRACING="true"             # Enable tracing by default
```

### CLI Usage

You can also control tracing via CLI flags:

```bash
# Enable tracing explicitly (even if LANGSMITH_TRACING is not set)
pr-agent review --trace

# Specify a custom project for this run
pr-agent review --trace --project "my-feature-branch"
```

## 4. Viewing Traces

Once a review runs with tracing enabled:
1. The CLI will output a link to the trace at the end of the run.
2. Click the link or go to your LangSmith project dashboard.
3. You can see:
   - Full input prompts sent to the LLM
   - Tool inputs and outputs (git diffs, test results)
   - Step-by-step latency and token usage
   - Any errors or exceptions

## Troubleshooting

- **No traces appearing?** Ensure `LANGSMITH_API_KEY` is set correctly and the `--trace` flag is used (or `LANGSMITH_TRACING=true` in env).
- **"Project not found"?** LangSmith automatically creates projects if they don't exist. Check your API key permissions.
