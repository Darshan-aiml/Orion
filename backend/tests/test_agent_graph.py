import pytest
from app.services.agent.graph import agent_graph

def test_agent_graph_execution():
    """
    Tests the LangGraph workflow without actually hitting OpenAI 
    (assuming OPENAI_API_KEY is missing or handled in the plan_resolution node).
    """
    initial_state = {
        "event_id": "test-123",
        "event_type": "ATTRACTION_CLOSED",
        "payload": {"attraction": "Eiffel Tower", "reason": "Weather"}
    }
    
    result = agent_graph.invoke(initial_state)
    
    assert result["event_id"] == "test-123"
    assert result["status"] in ["PLAN_PROPOSED", "PLAN_FAILED"]
    
    if result["status"] == "PLAN_PROPOSED":
        assert "reasoning_summary" in result
        assert "proposed_changes" in result
