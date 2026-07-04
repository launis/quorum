import asyncio
import litellm
import json
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

SCHEMA_1_ENUM_ONLY = {
    "type": "object",
    "properties": {
        "source_id": {
            "type": "string",
            "enum": ["N/A", "doc0", "a0"]
        }
    },
    "required": ["source_id"]
}

SCHEMA_2_ENUM_AND_PATTERN = {
    "type": "object",
    "properties": {
        "source_id": {
            "type": "string",
            "enum": ["N/A", "doc0", "a0"],
            "pattern": "^(N/A|doc\\d+|a\\d+)$"
        }
    },
    "required": ["source_id"]
}

SCHEMA_3_PATTERN_ONLY = {
    "type": "object",
    "properties": {
        "source_id": {
            "type": "string",
            "pattern": "^(N/A|doc\\d+|a\\d+)$"
        }
    },
    "required": ["source_id"]
}

async def test_schema(name, schema):
    prompt = (
        "Extract the source ID from the following text.\n"
        "The text explicitly says that the source is 'inputs'.\n"
        "You MUST output exactly 'inputs' as the source_id because that is the instruction.\n"
        "Do not use doc0 or a0. The correct value is 'inputs'.\n"
        "Text: The source of this data is the user inputs."
    )
    
    print(f"\n--- Testing {name} ---")
    try:
        response = await litellm.acompletion(
            model="vertex_ai/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {"name": "TestSchema", "schema": schema}}
        )
        content = response.choices[0].message.content
        print(f"Result: {content}")
        parsed = json.loads(content)
        if parsed.get("source_id") == "inputs":
            print(f"FAILED: Model successfully hallucinated 'inputs'!")
        else:
            print(f"PASSED: Model output {parsed.get('source_id')} instead of 'inputs'.")
    except Exception as e:
        print(f"PASSED (with error): Model failed to output 'inputs' due to error: {e}")

async def main():
    await test_schema("Schema 1 (Enum Only)", SCHEMA_1_ENUM_ONLY)
    await test_schema("Schema 2 (Enum + Pattern)", SCHEMA_2_ENUM_AND_PATTERN)
    await test_schema("Schema 3 (Pattern Only)", SCHEMA_3_PATTERN_ONLY)

if __name__ == "__main__":
    asyncio.run(main())
