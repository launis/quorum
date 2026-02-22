import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.getcwd())

from backend.llm.client import LLMClient
from backend.settings import get_settings


async def main():
    try:
        settings = get_settings()

        print(f"DEBUG: Default Strategy from Settings: {settings.default_model_strategy}")

        client = LLMClient()
        prompt_text = "mikä on tämä ohjelma"

        print(f"Running LLMClient.run_chat with prompt: '{prompt_text}'")
        print("Model argument is implicitly None (should resolve to default)")

        response = await client.run_chat(messages=[{"role": "user", "content": prompt_text}])

        print("\n--- RESPONSE ---")
        print(response)
        print("--- END RESPONSE ---")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
