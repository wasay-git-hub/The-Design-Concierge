import os
from src.backend.graphs.workflow import compiled_graph

def test_graph_real():
    print("Invoking graph with real image...")
    config = {"configurable": {"thread_id": "test_thread_real_123"}}
    image_path = r"C:\Users\wasay\The-Design-Concierge\static\uploads\463929c7-af7a-46bb-ab09-a66fe4d18462_room.png"
    compiled_graph.update_state(config, {"room_photo_url": image_path})
    state = compiled_graph.invoke(None, config)
    print("Graph completed!")
    print("Next node:", state.get("next_node"))

if __name__ == "__main__":
    test_graph_real()
