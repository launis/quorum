import sys
import json
from pydantic import BaseModel, ConfigDict, Field, create_model
from typing import Literal

AliasPattern = r"^(N/A|doc\d+|a\d+)$"
DocIdsLiteral = Literal["N/A", "doc0"]
QuoteIdsLiteral = Literal["N/A", "a0", "a1", "doc0"]

class LLMExtractedQuote(BaseModel):
    quote: str
    pass

DynamicLLMExtractedQuote = create_model(
    "DynamicLLMExtractedQuote",
    __base__=LLMExtractedQuote,
    source_id=(
        QuoteIdsLiteral,
        Field(
            ...,
            description="Auto-resolved document ID (e.g. doc0, a1)",
            json_schema_extra={"pattern": AliasPattern},
        ),
    ),
    __config__=ConfigDict(extra="ignore"),
)

class StepDTOStrictDynamic(BaseModel):
    exact_quotes: list[DynamicLLMExtractedQuote] = Field(default_factory=list)

class AtomResponse(StepDTOStrictDynamic):
    atom_id: str = Field(...)

class Final(BaseModel):
    evaluations: list[AtomResponse] = Field(...)

print(json.dumps(Final.model_json_schema(), indent=2))
