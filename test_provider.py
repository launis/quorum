import asyncio, os, sys
sys.path.append('c:/src/quorum')

from backend.llm.provider import LiteLLMProvider
from backend.models.domain.base import Metadata

async def test():
    print("Testing LiteLLMProvider...")
    os.environ["VERTEX_LOCATION"] = "europe-north1"
    
    # Needs valid credentials to work, but we can verify the tracking logic.
    provider = LiteLLMProvider("vertex_ai/gemini-2.5-flash", limits={"tpm": 1000, "rpm": 10})
    
    try:
        resp = await provider.generate(prompt="What is 1+1?", temperature=0.0, max_tokens=10)
        print(f"Usage: {resp.token_usage}")
        print(f"Cost: {resp.token_usage.get('total_cost')}")
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    asyncio.run(test())
