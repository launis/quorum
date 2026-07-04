import json
from typing import Annotated, Literal, Any
from pydantic import BaseModel, Field, create_model, ConfigDict

QuoteIdsLiteral = Literal["N/A", "doc0", "a0"]
PATTERN = r"^(N/A|doc\d+|a\d+)$"

class LLMExtractedQuote(BaseModel):
    pass

DynamicLLMExtractedQuote = create_model(
    "DynamicLLMExtractedQuote",
    __base__=LLMExtractedQuote,
    source_id=(
        QuoteIdsLiteral,
        Field(
            ...,
            description="Auto-resolved document ID (e.g. doc0, a1)",
            json_schema_extra={"pattern": r"^(N/A|doc\d+|a\d+)$"},
        ),
    ),
    __config__=ConfigDict(extra="ignore"),
)

class StepDTOStrictDynamic(BaseModel):
    exact_quotes: list[DynamicLLMExtractedQuote] = Field(default_factory=list)

print(json.dumps(StepDTOStrictDynamic.model_json_schema(), indent=2))
