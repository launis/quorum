import asyncio
from litellm import acompletion
import json
import copy

with open("scratch/schema_dump_real.json", "r") as f:
    schema = json.load(f)

# Fix exact_quotes source_id
schema["$defs"]["LLMExtractedQuote"]["properties"]["source_id"] = {
    "description": "Auto-resolved document ID",
    "title": "Source Id",
    "type": "string"
}

# Fix falsification_argument
schema["$defs"]["AtomResponseStrict"]["properties"]["falsification_argument"] = {
    "description": "Why this evidence might NOT satisfy the strict causal requirement of the rule.",
    "title": "Falsification Argument",
    "type": "string"
}

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
