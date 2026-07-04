import asyncio
from litellm import acompletion
import json
import copy

with open("scratch/schema_dump_real.json", "r") as f:
    schema = json.load(f)

# Replace exact_quotes with just a list of strings
schema["$defs"]["AtomResponseStrict"]["properties"]["exact_quotes"] = {
    "description": "Extract up to 3 physically contiguous sentences. Do not stitch them together. ABSOLUTE PRIORITY over contextual override. MUST be empty if contextual_override is True. You MUST always return a JSON object list format: `[{\"text\": \"...\"}]`. If the rule is a negative constraint and the text complies with it, return an empty list []. ",
    "items": {
        "type": "string"
    },
    "maxItems": 5,
    "title": "Exact Quotes",
    "type": "array"
}

# Remove LLMExtractedQuote from defs
if "LLMExtractedQuote" in schema["$defs"]:
    del schema["$defs"]["LLMExtractedQuote"]


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
        print("Success! Schema accepted by Vertex AI.")
        return True
    except Exception as e:
        print("Failed!")
        print(str(e))
        return False

if __name__ == "__main__":
    asyncio.run(test_schema(schema))
