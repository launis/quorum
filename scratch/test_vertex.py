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

def strip_enums(obj):
    if isinstance(obj, dict):
        if "enum" in obj:
            del obj["enum"]
        for k, v in list(obj.items()):
            strip_enums(v)
    elif isinstance(obj, list):
        for v in obj:
            strip_enums(v)

def reduce_max_items(obj, max_val):
    if isinstance(obj, dict):
        if "maxItems" in obj:
            obj["maxItems"] = min(obj["maxItems"], max_val)
        for k, v in obj.items():
            reduce_max_items(v, max_val)
    elif isinstance(obj, list):
        for v in obj:
            reduce_max_items(v, max_val)

async def bisect():
    print("Testing original...")
    if await test_schema(original_schema):
        print("Original passed? Unexpected.")
        return

    s1 = copy.deepcopy(original_schema)
    strip_enums(s1)
    if await test_schema(s1):
        print("Passed with enums stripped.")
        return
    else:
        print("Still fails without enums.")

    s2 = copy.deepcopy(s1)
    reduce_max_items(s2, 5)
    if await test_schema(s2):
        print("Passed with maxItems reduced to 5 globally.")
        return
    else:
        print("Still fails with maxItems=5.")

    s3 = copy.deepcopy(s1)
    reduce_max_items(s3, 3)
    if await test_schema(s3):
        print("Passed with maxItems reduced to 3 globally.")
        return
    else:
        print("Still fails with maxItems=3.")

    s4 = copy.deepcopy(s1)
    reduce_max_items(s4, 1)
    if await test_schema(s4):
        print("Passed with maxItems reduced to 1 globally.")
        return
    else:
        print("Still fails with maxItems=1.")
    
    # Try stripping specific fields from AtomResponseStrict
    s5 = copy.deepcopy(s4)
    del s5["$defs"]["AtomResponseStrict"]["properties"]["exact_quotes"]
    s5["$defs"]["AtomResponseStrict"]["required"].remove("exact_quotes")
    if await test_schema(s5):
        print("Passed by removing exact_quotes completely!")
        return

if __name__ == "__main__":
    asyncio.run(bisect())
