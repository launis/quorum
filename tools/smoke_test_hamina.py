import asyncio
import os
import litellm
from dotenv import load_dotenv

load_dotenv()

# Force location just in case
os.environ["VERTEX_LOCATION"] = "europe-north1"

async def test_hello():
    model = "vertex_ai/gemini-2.5-flash"
    print(f"Sending 'Hello' to {model} in europe-north1 (Hamina)...")
    
    try:
        response = await litellm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Hello! Reply strictly with: 'Hello from Hamina!'"}],
            vertex_location="europe-north1"
        )
        print("\n--- RESPONSE FROM AI ---")
        print(response.choices[0].message.content)
        print("------------------------")
        print("SUCCESS: Connection established.")
    except Exception as e:
        print("\n--- FAILURE ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hello())
