import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Vertex AI location environment variables for LiteLLM
os.environ["VERTEXAI_LOCATION"] = "global"
os.environ["VERTEX_LOCATION"] = "global"

async def test_call():
    try:
        from litellm import acompletion
        print("LiteLLM imported successfully.")
    except ImportError as e:
        print(f"Import Error: {e}")
        return

    print("Attempting LiteLLM call to vertex_ai/gemini-3.5-flash with vertex_location='global'...")
    try:
        response = await acompletion(
            model="vertex_ai/gemini-3.5-flash",
            messages=[{"role": "user", "content": "Say 'LiteLLM global ok' in 3 words."}],
            temperature=0.0,
            vertex_location="global"  # Pass parameter directly
        )
        print("\nSuccess!")
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("\nFailed to call model via LiteLLM:", e)

if __name__ == "__main__":
    asyncio.run(test_call())
