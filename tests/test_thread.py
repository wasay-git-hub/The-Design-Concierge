import concurrent.futures
from src.backend.nodes import analyze_room_photo_with_gpt4o

def test_in_thread():
    print("Testing in thread...")
    # Give it a tiny dummy image
    with open("dummy.jpg", "wb") as f:
        f.write(b"dummy image data")
    
    try:
        res = analyze_room_photo_with_gpt4o("dummy.jpg")
        print("Success:", res)
    except Exception as e:
        print("Error:", e)

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(test_in_thread)
    future.result()
