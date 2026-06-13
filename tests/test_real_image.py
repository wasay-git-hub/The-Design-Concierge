import os
from src.backend.graphs.nodes import analyze_room_photo_with_gpt4o

def test_real_image():
    print("Testing real image with Langfuse...")
    image_path = r"C:\Users\wasay\The-Design-Concierge\static\uploads\463929c7-af7a-46bb-ab09-a66fe4d18462_room.png"
    
    try:
        res = analyze_room_photo_with_gpt4o(image_path)
        print("Success:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_real_image()
