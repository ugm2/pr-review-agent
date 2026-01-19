import pytest
from unittest.mock import MagicMock
from pr_review_agent.agent.client import GroqClient
from pr_review_agent.schemas import ReviewRequest, ModelSettings

@pytest.fixture
def mock_groq_client():
    client = MagicMock(spec=GroqClient)
    client.chat_completion.return_value = '{"hypotheses": [], "tools": []}'
    return client

@pytest.fixture
def basic_review_request():
    return ReviewRequest(
        repo_root="/tmp/fake-repo",
        mode="staged",
        diff="diff --git a/file.py b/file.py...",
        settings=ModelSettings(verbose=False)
    )
