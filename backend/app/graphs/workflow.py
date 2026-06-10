from typing import TypedDict, List, Dict, Any, Union
from langgraph.graph import StateGraph, END
from backend.app.graphs.nodes import (
    node_welcome,
    node_vision_analysis,
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
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("welcome", node_welcome)
workflow.add_node("vision_analysis", node_vision_analysis)
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

# Compile Graph
compiled_graph = workflow.compile()
print("LangGraph Agentic Discovery Workflow successfully compiled.")
