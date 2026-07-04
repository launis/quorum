"""Comprehensive test: Try the REAL schema with varying description lengths
to isolate the exact contribution of verbose descriptions vs maxItems."""
import asyncio
from litellm import acompletion
import json
import copy

with open("scratch/schema_dump_real.json", "r") as f:
    original = json.load(f)

async def test_schema(label, schema_to_test):
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
        print(f"  [OK] {label}: PASS")
        return True
    except Exception:
        print(f"  [FAIL] {label}: FAIL")
        return False

def truncate_descriptions(obj, max_len):
    if isinstance(obj, dict):
        if "description" in obj and isinstance(obj["description"], str):
            obj["description"] = obj["description"][:max_len]
        for v in obj.values():
            truncate_descriptions(v, max_len)
    elif isinstance(obj, list):
        for v in obj:
            truncate_descriptions(v, max_len)

async def main():
    print("=== Test 1: Original schema (maxItems=18, full descriptions) ===")
    await test_schema("original", original)
    
    # Test 2: Original schema but truncate all descriptions to 50 chars
    print("\n=== Test 2: maxItems=18, descriptions truncated to 50 chars ===")
    s2 = copy.deepcopy(original)
    truncate_descriptions(s2, 50)
    await test_schema("trunc-50", s2)
    
    # Test 3: Original schema but truncate all descriptions to 20 chars
    print("\n=== Test 3: maxItems=18, descriptions truncated to 20 chars ===")
    s3 = copy.deepcopy(original)
    truncate_descriptions(s3, 20)
    await test_schema("trunc-20", s3)
    
    # Test 4: Original schema, no descriptions at all
    print("\n=== Test 4: maxItems=18, NO descriptions ===")
    s4 = copy.deepcopy(original)
    def strip_desc(obj):
        if isinstance(obj, dict):
            obj.pop("description", None)
            for v in obj.values():
                strip_desc(v)
        elif isinstance(obj, list):
            for v in obj:
                strip_desc(v)
    strip_desc(s4)
    await test_schema("no-desc", s4)
    
    # Test 5: maxItems=8 with full descriptions
    print("\n=== Test 5: maxItems=8, full descriptions ===")
    s5 = copy.deepcopy(original)
    s5["properties"]["evaluations"]["maxItems"] = 8
    await test_schema("maxItems-8-full-desc", s5)
    
    # Test 6: maxItems=7 with full descriptions (proven threshold)
    print("\n=== Test 6: maxItems=7, full descriptions ===")
    s6 = copy.deepcopy(original)
    s6["properties"]["evaluations"]["maxItems"] = 7
    await test_schema("maxItems-7-full-desc", s6)
    
    # Test 7: maxItems=10, descriptions truncated to 50 chars
    print("\n=== Test 7: maxItems=10, descriptions truncated to 50 chars ===")
    s7 = copy.deepcopy(original)
    s7["properties"]["evaluations"]["maxItems"] = 10
    truncate_descriptions(s7, 50)
    await test_schema("maxItems-10-trunc-50", s7)
    
    # Test 8: maxItems=12, NO descriptions
    print("\n=== Test 8: maxItems=12, NO descriptions ===")
    s8 = copy.deepcopy(original)
    s8["properties"]["evaluations"]["maxItems"] = 12
    strip_desc(s8)
    await test_schema("maxItems-12-no-desc", s8)
    
    # Test 9: maxItems=18, NO descriptions, NO anyOf (no nullable)
    print("\n=== Test 9: maxItems=18, NO descriptions, NO anyOf ===")
    s9 = copy.deepcopy(original)
    def strip_anyof(obj):
        if isinstance(obj, dict):
            if "anyOf" in obj:
                # Replace with just the first non-null type
                for opt in obj["anyOf"]:
                    if opt.get("type") != "null":
                        obj.update(opt)
                        break
                del obj["anyOf"]
            for v in list(obj.values()):
                strip_anyof(v)
        elif isinstance(obj, list):
            for v in obj:
                strip_anyof(v)
    strip_desc(s9)
    strip_anyof(s9)
    await test_schema("maxItems-18-no-desc-no-anyof", s9)

if __name__ == "__main__":
    asyncio.run(main())
