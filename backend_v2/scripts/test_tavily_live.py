"""Manual smoke test for Tavily AI Search.

Run: python backend_v2/scripts/test_tavily_live.py "search query here"

Requires TAVILY_API_KEY in .env file.
This script is NOT part of the pytest suite (Tavily No-Spam policy).
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_v2.services.mcp.tavily_search_client import tavily_search


async def main() -> None:
    """Execute a live Tavily search."""
    if len(sys.argv) < 2:
        print("Usage: python backend_v2/scripts/test_tavily_live.py 'your search query'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"\n🔍 Searching Tavily for: '{query}'...\n")

    result = await tavily_search(query)

    print("✅ Result:")
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
    print(f"\n⏱️ Duration: {result.duration_ms}ms")
    print(f"📎 Sources: {len(result.source_urls)}")


if __name__ == "__main__":
    asyncio.run(main())
