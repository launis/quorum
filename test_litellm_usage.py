import asyncio
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

from litellm import acompletion, completion_cost

async def test_llm():
    try:
        response = await acompletion(
            model='vertex_ai/gemini-2.5-flash', 
            messages=[{'role': 'user', 'content': 'Hello, output exactly 10 tokens.'}], 
            max_tokens=10
        )
        with open("c:\\src\\quorum\\test_usage.log", "w", encoding="utf-8") as f:
            f.write("--- USAGE OBJECT ---\n")
            f.write(str(response.usage))
            f.write("\n\n--- USAGE DICT / DUMP ---\n")
            if hasattr(response.usage, 'model_dump'):
                dump = response.usage.model_dump()
                f.write(json.dumps(dump, indent=2))
            elif hasattr(response.usage, '__dict__'):
                dump = vars(response.usage)
                f.write(json.dumps(dump, indent=2))
            else:
                f.write(str(response.usage))
                
            f.write("\n\n--- COST ---\n")
            cost = completion_cost(completion_response=response, model='gemini-2.5-flash')
            f.write(f"Cost USD: {cost}\n")
        
        print("Success, wrote to test_usage.log")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
