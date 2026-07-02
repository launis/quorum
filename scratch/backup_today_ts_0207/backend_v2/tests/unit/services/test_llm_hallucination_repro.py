import pytest
from pydantic import ConfigDict, Field, ValidationError, create_model


def test_llm_hallucination_validation_error_repro():
    # 1. Simulate the dynamic schema for the matrix evaluation using Pydantic Alias Pattern
    # The expected block ID is blk_2cbe96bffde04571, but the alias is eval_1
    StrictDynamicSchema = create_model(
        "StrictDynamicMatrixEvaluation",
        blk_2cbe96bffde04571=(str, Field(..., alias="eval_1")),
        __config__=ConfigDict(extra="forbid", populate_by_name=True),
    )

    # 2. Check JSON Schema (LLM will see eval_1, NOT blk_2cbe...)
    schema_json = StrictDynamicSchema.model_json_schema()
    assert "eval_1" in schema_json["properties"]
    assert "blk_2cbe96bffde04571" not in schema_json["properties"]

    # 3. Simulate the LLM providing the safe alias eval_1
    llm_alias_payload = {"eval_1": "DATA_CHECKED_AND_SECURED"}

    # 4. TDD GREEN: This should parse perfectly
    result = StrictDynamicSchema(**llm_alias_payload)

    # 5. Verify the backend successfully translated it back to the ID
    assert getattr(result, "blk_2cbe96bffde04571", None) == "DATA_CHECKED_AND_SECURED"

    # 6. Verify that an older hallucination attempting to use an extra key still crashes
    with pytest.raises(ValidationError) as exc_info:
        StrictDynamicSchema(**{"eval_1": "OK", "eval_74571": "EXTRA"})
    assert "Extra inputs are not permitted" in str(exc_info.value)
