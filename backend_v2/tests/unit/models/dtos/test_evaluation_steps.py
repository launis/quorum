from typing import Annotated, Literal

import pytest
from pydantic import ConfigDict, Field, ValidationError, create_model

from backend_v2.models.dtos.evaluation_steps import (
    BaseExtractionDTO,
    ParsingLogStepsSemantic,
    ParsingLogStepsStrict,
    StepDTOSemantic,
    StepDTOStrict,
)


def test_step_dto_strict_validation() -> None:
    """Verify validation of StepDTOStrict with the new cognitive pipeline fields."""
    data = {
        "rule_internalization": "Criteria require checking X.",
        "used_source_aliases": [],
        "source_document_aliases": ["doc_123"],
        "exact_quotes": [{"source_id": "doc_123", "text": "This is a verbatim quote."}],
        "reasoning_steps": "1) Rule requires X. 2) Text has X. 3) Pass.",
        "falsification_argument": "This could fail if text is fake.",
        "decision": True,
        "semantic_reasoning": "Standard verification pass.",
    }
    obj = StepDTOStrict.model_validate(data, context={"alias_map": {"doc_123": "doc_123"}})
    assert obj.rule_internalization == "Criteria require checking X."
    assert obj.source_document_aliases == ["doc_123"]
    assert obj.exact_quotes[0].text == "This is a verbatim quote."
    assert obj.decision is True

    # Verify that deleted fields (like structural_location, counter_quote) trigger extra_forbidden
    invalid_data = data.copy()
    invalid_data["structural_location"] = "Page 1"
    with pytest.raises(ValidationError) as exc:
        StepDTOStrict.model_validate(invalid_data, context={"alias_map": {"doc_123": "doc_123"}})
    assert "extra_forbidden" in str(exc.value)


def test_step_dto_semantic_validation() -> None:
    """Verify validation of StepDTOSemantic with contextual overrides."""
    # Test valid contextual override
    data = {
        "rule_internalization": "Criteria require checking X.",
        "used_source_aliases": [],
        "source_document_aliases": ["doc_123"],
        "exact_quotes": [],
        "reasoning_steps": "1) Rule requires X. 2) Text has X. 3) Pass.",
        "falsification_argument": "This could fail if text is fake.",
        "decision": True,
        "semantic_reasoning": "Standard verification pass.",
        "contextual_override": True,
        "override_reason": "Implied semantic match.",
    }
    obj = StepDTOSemantic.model_validate(data)
    assert obj.contextual_override is True
    assert obj.override_reason == "Implied semantic match."
    assert obj.exact_quotes == []

    # Test validator raises ValidationError if exact_quotes is non-empty when contextual_override is True
    data["exact_quotes"] = [{"source_id": "doc_123", "text": "Some quote"}]
    with pytest.raises(ValidationError) as exc:
        StepDTOSemantic.model_validate(data)
    assert "Null hypothesis violation" in str(exc.value)


def test_step_dto_alias_sanitization() -> None:
    """Verify that typos (src3) and hallucinations (src_5) are sanitized before Literal validation."""
    # Simulate SchemaFactory behavior including Annotated wrapper on item_type
    DocIdsLiteral = Annotated[Literal["src_0", "src_1", "N/A"], Field(description="Doc ID")]
    DynStrict = create_model(
        "DynStrict",
        __base__=StepDTOStrict,
        source_document_aliases=(
            list[DocIdsLiteral],
            Field(...),
        ),
        __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
    )

    data = {
        "rule_internalization": "Criteria require checking X.",
        "source_document_aliases": ["src_0", "src1", "src_5", "invalid"],
        "exact_quotes": [],
        "reasoning_steps": "1) Check. 2) Done.",
        "falsification_argument": "None",
        "decision": True,
        "semantic_reasoning": "Standard pass.",
    }

    # This should succeed after the fix by transforming aliases to ['src_0', 'src_1', 'N/A', 'N/A']
    obj = DynStrict.model_validate(data)
    assert obj.source_document_aliases == ["src_0", "src_1", "N/A", "N/A"]
    assert obj.used_source_aliases == []


def test_base_extraction_dto_negative_and_boundary_cases() -> None:
    """Verify negative input types, non-string list elements, and missing model fields in BaseExtractionDTO."""
    # 1. Negative test: non-dictionary input raises ValidationError
    with pytest.raises(ValidationError) as exc_info:
        BaseExtractionDTO.model_validate(12345)
    assert "Expected dictionary input for validation" in str(exc_info.value)

    # 2. Negative test: unmapped source_document_aliases on BaseExtractionDTO (field not in BaseExtractionDTO.model_fields)
    with pytest.raises(ValidationError) as exc_extra:
        BaseExtractionDTO.model_validate({"source_document_aliases": ["src_0"]})
    assert "extra_forbidden" in str(exc_extra.value)

    # 3. Negative test: non-string item inside used_source_aliases triggers strict type error after passthrough
    with pytest.raises(ValidationError) as exc_item:
        BaseExtractionDTO.model_validate({"used_source_aliases": [123]})
    assert "string_type" in str(exc_item.value)


def test_parsing_log_steps_envelopes() -> None:
    """Verify ParsingLogStepsStrict and ParsingLogStepsSemantic envelope validation and negative cases."""
    strict_step = {
        "rule_internalization": "Check X.",
        "source_document_aliases": ["doc_1"],
        "exact_quotes": [],
        "reasoning_steps": "1) X.",
        "decision": False,
        "semantic_reasoning": "Failed.",
    }
    strict_log = ParsingLogStepsStrict.model_validate({"steps": [strict_step]})
    assert len(strict_log.steps) == 1
    assert strict_log.steps[0].decision is False

    semantic_step = {
        **strict_step,
        "decision": True,
        "contextual_override": True,
        "override_reason": "Override applied.",
    }
    semantic_log = ParsingLogStepsSemantic.model_validate({"steps": [semantic_step]})
    assert len(semantic_log.steps) == 1
    assert semantic_log.steps[0].contextual_override is True

    # Negative test: missing required steps field
    with pytest.raises(ValidationError):
        ParsingLogStepsStrict.model_validate({})

