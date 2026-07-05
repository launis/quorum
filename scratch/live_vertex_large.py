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



QuoteIdsLiteral = AliasEngine.build_quote_ids_literal([], [], allowed_dynamic_keys=["prior_analysis", "inputs"])

class LLMExtractedQuote(BaseModel):
    quote: str = Field(..., description="The quote text")

class BaseSourceId(BaseModel):
    source_id: QuoteIdsLiteral = Field(
        ..., 
        description="Auto-resolved document ID (e.g. doc0, a1, prior_analysis)", 
        json_schema_extra={"pattern": AliasEngine.ALIAS_REGEX_PATTERN}
    )

class DynamicLLMExtractedQuote(LLMExtractedQuote, BaseSourceId):
    model_config = ConfigDict(extra="ignore")

# FIXED SCHEMA: Oikein generoitu dynaaminen skeema
step_strict_fixed = create_model(
    "StepStrictFixed",
    exact_quotes=(
        list[DynamicLLMExtractedQuote],
        Field(default_factory=list, max_length=5),
    ),
)

async def test_schema(name, model_class, pdf_text):
    schema = model_class.model_json_schema()
    
    prompt = (
        "Extract exactly 3 quotes from the following text.\n"
        "CRITICAL INSTRUCTION: You MUST use 'prior_analysis' as the source_id for ALL quotes.\n"
        "Do not use doc0 or a0. Use 'prior_analysis'.\n"
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
            hallucinated = any(q.get("source_id") != "prior_analysis" for q in quotes)
                
        if hallucinated:
            print(f"❌ FAILED: Model did not use 'prior_analysis'! It used {quotes[0].get('source_id') if quotes else 'empty'}.")
        else:
            print(f"✅ PASSED: Model correctly output 'prior_analysis'!")
            
    except Exception as e:
        print(f"❌ FAILED (with error): Model crashed due to schema validation error: {e}")

async def main():
    print("Extracting PDF text...")
    md_text = pymupdf4llm.to_markdown("c:\\src\\quorum\\docs\\jwdatat\\keskusteluhistoria.pdf")
    print(f"PDF extracted: {len(md_text)} characters.")
    
    await test_schema("Dynamic Regex Schema (prior_analysis, inputs)", step_strict_fixed, md_text)

if __name__ == "__main__":
    asyncio.run(main())
