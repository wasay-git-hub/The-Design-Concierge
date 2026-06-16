import pytest
from src.backend.workflow import route_conversation

def test_route_conversation_incomplete():
    """
    Test that if the state is NOT marked as complete, 
    the router follows the 'next_node' value.
    """
    mock_state = {
        "is_complete": False,
        "next_node": "vision_analysis"
    }
    
    # We pass mock_state as if it were the AgentState dictionary
    result = route_conversation(mock_state)
    assert result == "vision_analysis", f"Expected 'vision_analysis', but got {result}"

def test_route_conversation_complete():
    """
    Test that if the state IS marked as complete, 
    the router jumps directly to the 'synthesis' phase.
    """
    mock_state = {
        "is_complete": True,
        "next_node": "vision_analysis" # This should be ignored
    }
    
    result = route_conversation(mock_state)
    assert result == "synthesis", f"Expected 'synthesis', but got {result}"

def test_route_conversation_default():
    """
    Test that if next_node is not specified and is_complete is False,
    the router falls back to 'welcome'.
    """
    mock_state = {
        "is_complete": False
        # next_node omitted
    }
    
    result = route_conversation(mock_state)
    assert result == "welcome", f"Expected 'welcome', but got {result}"
