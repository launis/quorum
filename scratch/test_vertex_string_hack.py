import asyncio
from litellm import acompletion
import json
import copy

with open("scratch/schema_dump_real.json", "r") as f:
    schema = json.load(f)

# Hide exact_quotes inside a string to avoid nested array state explosion in Vertex AI
schema["$defs"]["AtomResponseStrict"]["properties"]["exact_quotes"] = {
    "description": "Extract up to 3 physically contiguous sentences. MUST be a JSON array string like '[{\"text\": \"...\"}]'.",
    "title": "Exact Quotes",
    "type": "string"
}

# Clean up the definition
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
