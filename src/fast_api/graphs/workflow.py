from typing import List, Dict, Any, Union, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
from src.fast_api.graphs.nodes import (
    node_welcome,
    node_vision_analysis,
    node_visual_taste_test,
    node_refinement,
    node_synthesis
)

# 1. State Definition
class AgentState(TypedDict):
    # Client basic info
    client_id: str
    name: str
    email: str
    phone: str
    
    # Project characteristics
    location: str
    room_type: str
    area_sqft: int
    scope_level: int
    material_tier: int
    
    # Financial Estimates
    budget_min: float
    budget_max: float
    
    # Readiness Metrics
    readiness_score: int
    timeline: str
    decision_maker: str
    
    # Multi-Modal Vision Analysis
    room_photo_url: str
    vision_analysis: Dict[str, Any]
    
    # Refined Design preferences
    preferred_visual_style: str
    design_dna: str
    
    # Conversation log state
    chat_history: List[Dict[str, str]]
    
    # State routing controls
    next_node: str
    current_question: str
    is_complete: bool

# 2. State Routing Helper
def route_conversation(state: AgentState) -> str:
    """
    Decides the next node to transition to.
    If the state is marked as complete, we jump to synthesis.
    Otherwise, we follow the next_node parameter stored in state.
    """
    if state.get("is_complete"):
        return "synthesis"
    
    return state.get("next_node", "welcome")

# 3. Build Graph
workflow = StateGraph(AgentState)  # type: ignore

# Add Nodes
workflow.add_node("welcome", node_welcome)
workflow.add_node("vision_analysis", node_vision_analysis)
workflow.add_node("visual_taste_test", node_visual_taste_test)
workflow.add_node("refinement", node_refinement)
workflow.add_node("synthesis", node_synthesis)

# Set up edges
workflow.set_entry_point("welcome")

# Linear routing for onboarding setup
workflow.add_conditional_edges(
    "welcome",
    route_conversation,
    {
        "welcome": "welcome",
        "vision_analysis": "vision_analysis"
    }
)

workflow.add_conditional_edges(
    "vision_analysis",
    route_conversation,
    {
        "vision_analysis": "vision_analysis",
        "visual_taste_test": "visual_taste_test"
    }
)

workflow.add_conditional_edges(
    "visual_taste_test",
    route_conversation,
    {
        "visual_taste_test": "visual_taste_test",
        "refinement": "refinement"
    }
)

# Refinement can loop on itself or move to synthesis once sufficient state is gathered
workflow.add_conditional_edges(
    "refinement",
    route_conversation,
    {
        "refinement": "refinement",
        "synthesis": "synthesis"
    }
)

# Synthesis transitions to END
workflow.add_edge("synthesis", END)

# Compile Graph with Checkpointer and Breakpoints
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
db_path = os.path.join(root_dir, "data", "checkpoints.sqlite")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

compiled_graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["vision_analysis", "refinement", "synthesis"]
)
print("LangGraph Agentic Discovery Workflow successfully compiled with production Checkpointer.")
