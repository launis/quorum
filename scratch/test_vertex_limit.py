import asyncio
from litellm import acompletion
import json
import copy

with open("scratch/schema_dump_real.json", "r") as f:
    original_schema = json.load(f)

async def test_schema(schema_to_test):
    try:
        response = await acompletion(
            model="vertex_ai/gemini-2.5-flash",
            messages=[{"role": "user", "content": "test"}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "TestSchema",
                    "schema": schema_to_test,
                    "strict": True
                }
            }
        )
        return True
    except Exception as e:
        return False

async def find_max():
    for limit in range(18, 0, -1):
        s = copy.deepcopy(original_schema)
        # Modify ONLY evaluations maxItems
        s["properties"]["evaluations"]["maxItems"] = limit
        
        if await test_schema(s):
            print(f"Vertex AI accepts evaluations maxItems = {limit}")
            break
        else:
            print(f"Failed at {limit}")

if __name__ == "__main__":
    asyncio.run(find_max())
