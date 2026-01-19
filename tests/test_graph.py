import pytest
import json
from unittest.mock import MagicMock
from pr_review_agent.agent.graph import ReviewGraph
from pr_review_agent.schemas import AgentState

class TestReviewGraph:
    def test_plan_step(self, mock_groq_client, basic_review_request):
        graph = ReviewGraph(basic_review_request, mock_groq_client)
        state = AgentState(diff="foo", changed_files=["foo.py"])
        
        # Mock LLM response to return a plan
        mock_groq_client.chat_completion.return_value = json.dumps({
            "hypotheses": ["Maybe a bug"],
            "tools": [{"name": "run_command", "args": {"command": "ls"}}]
        })
        
        updates = graph.plan_step(state)
        
        assert "hypotheses" in updates
        assert len(updates["candidates"]) == 1
        assert updates["candidates"][0]["name"] == "run_command"

    def test_execute_tools_step(self, mock_groq_client, basic_review_request):
        graph = ReviewGraph(basic_review_request, mock_groq_client)
        state = AgentState(
            diff="foo", 
            candidates=[{"name": "run_command", "args": {"command": "echo test"}}],
            iteration=0
        )
        
        # We need to test that it actually tries to run the tool.
        # Since tools are invoked, we might want to patch the tools in the module if we want to isolate completely,
        # but for this integration-like test, checking it returns observations is good.
        
        results = graph.execute_tools_step(state)
        
        assert "tool_observations" in results
        assert results["iteration"] == 1
        assert len(results["tool_observations"]) == 1
        assert results["tool_observations"][0]["tool"] == "run_command"

    def test_should_continue(self, mock_groq_client, basic_review_request):
        graph = ReviewGraph(basic_review_request, mock_groq_client)
        
        # Case 1: Has candidates -> tools
        state_tools = AgentState(diff="", candidates=[{"name": "foo"}])
        assert graph.should_continue(state_tools) == "tools"
        
        # Case 2: No candidates -> review
        state_review = AgentState(diff="", candidates=[])
        assert graph.should_continue(state_review) == "review"
