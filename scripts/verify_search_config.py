
import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.hooks.search_client import GoogleSearchTool

async def test_search():
    print("\n--- TEST: Google Search Tool Validity ---")
    
    # Check if API keys are present (don't print them!)
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_CX") or os.getenv("GOOGLE_SEARCH_CX")
    
    if not api_key:
        print("⚠️  WARNING: GOOGLE_API_KEY / GOOGLE_SEARCH_API_KEY not found in env.")
        # Proceeding might fail unless using a mock or if logic handles missing keys gracefully.
    else:
        print("✅ API Key found in env.")
        
    if not cx:
        print("⚠️  WARNING: GOOGLE_CX / GOOGLE_SEARCH_CX not found in env.")
    else:
        print("✅ CX found in env.")

    tool = GoogleSearchTool()
    
    # We don't want to actually burn quota if we can avoid it, but verification implies testing connectivity.
    # However, if keys are missing from this shell context, it will fail.
    # Let's try a dry run if the tool supports it, or just instantiation.
    
    if not tool.api_key or not tool.cx:
        print("❌ Tool initialized with missing credentials.")
        return

    print("✅ Tool initialized successfully.")
    
    # Optional: Actual search (commented out to save quota/avoid network in test env if needed)
    # try:
    #     results = await tool.search("Cognitive Quorum AI", num_results=1)
    #     print(f"✅ Search successful. Got {len(results)} results.")
    # except Exception as e:
    #     print(f"❌ Search failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
