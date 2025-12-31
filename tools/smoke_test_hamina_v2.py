import asyncio
import os
import litellm
from dotenv import load_dotenv

load_dotenv()
os.environ["VERTEX_LOCATION"] = "europe-north1"

async def test_hello():
    model = "vertex_ai/gemini-2.5-flash"
    print(f"Sending 'Hello' to {model} in europe-north1...")
    
    with open("smoke_test_output.txt", "w", encoding="utf-8") as f:
        try:
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": "Hello! Reply strictly with: 'Hello from Hamina!'"}],
                vertex_location="europe-north1"
            )
            content = response.choices[0].message.content
            print(f"RECEIVED: {content}")
            f.write(f"SUCCESS\nModel: {model}\nLocation: europe-north1\nResponse: {content}\n")
        except Exception as e:
            print(f"ERROR: {e}")
            f.write(f"FAILURE\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_hello())
