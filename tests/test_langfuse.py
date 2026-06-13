import os
from dotenv import load_dotenv

load_dotenv()

from langfuse.openai import OpenAI

try:
    print("Testing exactly like nodes.py...")
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": "Output JSON"}],
        max_completion_tokens=1000,
        temperature=0.2
    )
    print("Success!", response)
except Exception as e:
    print("Exception caught:", e)
