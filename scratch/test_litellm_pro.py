import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Vertex AI location environment variables for LiteLLM
os.environ["VERTEXAI_LOCATION"] = "global"
os.environ["VERTEX_LOCATION"] = "global"

async def test_call_pro():
    try:
        from litellm import acompletion
        print("LiteLLM imported successfully.")
    except ImportError as e:
        print(f"Import Error: {e}")
        return

    print("Attempting a genuine reasoning query to vertex_ai/gemini-3.5-pro via global region...")
    prompt = (
        "Explain in Finnish (exactly two concise paragraphs) how your advanced Gemini 3.5 Pro "
        "reasoning engine solves complex software architecture and strict code audit tasks "
        "compared to previous models."
    )
    
    try:
        response = await acompletion(
            model="vertex_ai/gemini-3.5-pro",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            vertex_location="global"  # Pass vertex_location directly to ensure global endpoint routing
        )
        print("\n=== SUCCESS: RESPONSE FROM GEMINI 3.5 PRO ===")
        print(response.choices[0].message.content)
        print("=============================================")
    except Exception as e:
        print("\nFailed to call Gemini 3.5 Pro via LiteLLM:", e)

if __name__ == "__main__":
    asyncio.run(test_call_pro())
