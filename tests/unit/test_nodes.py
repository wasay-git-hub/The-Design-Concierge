import pytest
from src.backend.nodes import node_welcome

def test_node_welcome():
    """
    Test that the welcome node initializes the conversation
    with the correct initial state.
    """
    mock_state = {
        "chat_history": []
    }
    
    result = node_welcome(mock_state)
    
    # Assertions
    assert result["next_node"] == "vision_analysis"
    assert result["is_complete"] == False
    assert "Please upload a photo" in result["current_question"]
    
    # The chat history should have an assistant message
    assert len(result["chat_history"]) == 1
    assert result["chat_history"][0]["role"] == "assistant"
    assert "Please upload a photo" in result["chat_history"][0]["content"]
