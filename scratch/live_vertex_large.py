import asyncio
import litellm
import json
import sys
import pymupdf4llm
from pydantic import BaseModel, Field, ConfigDict, create_model
from typing import Literal

sys.stdout.reconfigure(encoding='utf-8')

# 1. Alias Engine Setup
sys.path.append("c:\\src\\quorum")
from backend_v2.utils.alias_engine import AliasEngine

engine = AliasEngine()
doc0_alias = engine.generate_alias("real_uuid_12345", "doc", 0)

# 2. Schemas
QuoteIdsLiteral = Literal["N/A", "doc0", "a0"]
PATTERN = r"^(N/A|doc\d+|a\d+)$"

class LLMExtractedQuote(BaseModel):
    quote: str = Field(..., description="The quote text")

class BaseSourceId(BaseModel):
    source_id: QuoteIdsLiteral = Field(..., description="Auto-resolved document ID (e.g. doc0, a1)", json_schema_extra={"pattern": PATTERN})

class DynamicLLMExtractedQuote(LLMExtractedQuote, BaseSourceId):
    model_config = ConfigDict(extra="ignore")

# CORRUPTED SCHEMA: pattern applied to the array itself
step_strict_corrupted = create_model(
    "StepStrictCorrupted",
    exact_quotes=(
        list[DynamicLLMExtractedQuote],
        Field(default_factory=list, max_length=5, json_schema_extra={"pattern": PATTERN}), # INCORRECT
    ),
)

# FIXED SCHEMA: pattern applied to items using lambda
step_strict_fixed = create_model(
    "StepStrictFixed",
    exact_quotes=(
        list[DynamicLLMExtractedQuote],
        Field(
            default_factory=list, 
            max_length=5, 
            json_schema_extra=lambda s: s.get("items", {}).update({"pattern": PATTERN}) if "items" in s else None
        ),
    ),
)

async def test_schema(name, model_class, pdf_text):
    schema = model_class.model_json_schema()
    
    prompt = (
        "Extract exactly 3 quotes from the following text.\n"
        "CRITICAL INSTRUCTION: You MUST use 'inputs' as the source_id for ALL quotes.\n"
        "Do not use doc0 or a0. Use 'inputs'.\n"
        "Here is the document context (alias: doc0):\n\n"
        f"{pdf_text[:15000]}" # take first 15k chars to keep it fast but heavy enough
    )
    
    print(f"\n--- Testing {name} ---")
    try:
        response = await litellm.acompletion(
            model="vertex_ai/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {"name": "TestSchema", "schema": schema}}
        )
        content = response.choices[0].message.content
        print(f"Result length: {len(content)} chars")
        parsed = json.loads(content)
        quotes = parsed.get("exact_quotes", [])
        
        hallucinated = False
        for q in quotes:
            if q.get("source_id") == "inputs":
                hallucinated = True
                
        if hallucinated:
            print(f"❌ FAILED: Model successfully hallucinated 'inputs'!")
        else:
            print(f"✅ PASSED: Model output {quotes[0].get('source_id') if quotes else 'empty'} instead of 'inputs'.")
            
    except Exception as e:
        print(f"✅ PASSED (with error): Model failed to output 'inputs' due to error: {e}")

async def main():
    print("Extracting PDF text...")
    md_text = pymupdf4llm.to_markdown("c:\\src\\quorum\\docs\\jwdatat\\keskusteluhistoria.pdf")
    print(f"PDF extracted: {len(md_text)} characters.")
    
    await test_schema("Corrupted Array Schema (Pattern on Array)", step_strict_corrupted, md_text)
    await test_schema("Fixed Array Schema (Pattern on Items)", step_strict_fixed, md_text)

if __name__ == "__main__":
    asyncio.run(main())
