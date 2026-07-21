"""Unit tests for the EPIC 56 Dynamic Pydantic DTO Factory."""

from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.services.orchestrator.extraction_schema_factory import create_extraction_model


def test_create_extraction_model_deterministic_sorting() -> None:
    """Test that sorting facts ensures identical schemas and deterministic field ordering."""
    facts_1 = ["banana", "apple", "cherry"]
    facts_2 = ["cherry", "apple", "banana", "banana"]  # with duplicate

    model_1 = create_extraction_model(facts_1)
    model_2 = create_extraction_model(facts_2)

    data = {
        "chunk_index": 0,
        "context_scan_trace": "Everything matched fine.",
        "search_context_anchor": None,
        "extracted_facts": {
            "apple": "Found apple",
            "banana": None,
            "cherry": "Found cherry",
        },
    }

    inst_1: Any = model_1.model_validate(data)
    inst_2: Any = model_2.model_validate(data)

    assert inst_1.extracted_facts.apple == "Found apple"
    assert inst_2.extracted_facts.apple == "Found apple"
    assert list(inst_1.extracted_facts.model_fields.keys()) == ["apple", "banana", "cherry"]
    assert list(inst_2.extracted_facts.model_fields.keys()) == ["apple", "banana", "cherry"]


def test_schema_tracks() -> None:
    """Test that EXTRACTIVE_SENSOR and COGNITIVE_JUDGEMENT tracks generate correct schemas."""
    model_extractive = create_extraction_model(["fact_a"], track="EXTRACTIVE_SENSOR")
    model_cognitive = create_extraction_model(["fact_a"], track="COGNITIVE_JUDGEMENT")

    # Extractive model should NOT have validation_decision
    assert "validation_decision" not in model_extractive.model_fields

    # Cognitive model MUST have validation_decision
    assert "validation_decision" in model_cognitive.model_fields

    # Validate cognitive passes with validation_decision
    data_cog = {
        "chunk_index": 0,
        "context_scan_trace": "Reasoning trace",
        "search_context_anchor": None,
        "validation_decision": True,
        "extracted_facts": {"fact_a": "value"},
    }
    cog_instance: Any = model_cognitive.model_validate(data_cog)
    assert cog_instance.validation_decision is True

    # Validate cognitive fails without validation_decision
    data_cog_missing = data_cog.copy()
    del data_cog_missing["validation_decision"]
    with pytest.raises(ValidationError):
        model_cognitive.model_validate(data_cog_missing)


def test_canonicalise_nulls() -> None:
    """Test that cosmetic placeholders are successfully mapped to None silently."""
    model = create_extraction_model(["fact_a", "fact_b"])
    data = {
        "chunk_index": 0,
        "context_scan_trace": "none",
        "search_context_anchor": "N/A",
        "extracted_facts": {
            "fact_a": "none",
            "fact_b": "",
        },
    }

    inst: Any = model.model_validate(data)
    assert inst.search_context_anchor is None
    assert inst.extracted_facts.fact_a is None
    assert inst.extracted_facts.fact_b is None


def test_lazy_dumping_ban() -> None:
    """Test that quotes longer than 80% of source_text are rejected."""
    model = create_extraction_model(["fact_a"])
    source_text = "This is a short source text."  # length 28 characters
    long_fact = "12345678901234567890123"  # length 23 (> 0.80 * 28)
    short_fact = "123"

    # Should pass without context
    data = {
        "chunk_index": 0,
        "context_scan_trace": "Trace",
        "search_context_anchor": None,
        "extracted_facts": {"fact_a": long_fact},
    }
    model.model_validate(data)

    # Should pass with context if within limit
    data_short = {
        "chunk_index": 0,
        "context_scan_trace": "Trace",
        "search_context_anchor": None,
        "extracted_facts": {"fact_a": short_fact},
    }
    model.model_validate(data_short, context={"source_text": source_text})

    # Should fail if quote length > 80% of source_text
    with pytest.raises(ValidationError) as exc:
        model.model_validate(data, context={"source_text": source_text})
    assert "Lazy dumping detected for fact" in str(exc.value)

    # Should also fail if search_context_anchor exceeds 80%
    data_anchor_fail = {
        "chunk_index": 0,
        "context_scan_trace": "Trace",
        "search_context_anchor": long_fact,
        "extracted_facts": {"fact_a": short_fact},
    }
    with pytest.raises(ValidationError) as exc:
        model.model_validate(data_anchor_fail, context={"source_text": source_text})
    assert "Lazy dumping detected for search_context_anchor" in str(exc.value)


def test_extra_forbid() -> None:
    """Test that extra fields are strictly forbidden."""
    model = create_extraction_model(["fact_a"])

    # Extra field in root
    with pytest.raises(ValidationError):
        model.model_validate(
            {
                "chunk_index": 0,
                "context_scan_trace": "Trace",
                "search_context_anchor": None,
                "extracted_facts": {"fact_a": "value"},
                "extra_field": "forbidden",
            }
        )

    # Extra field in extracted_facts
    with pytest.raises(ValidationError):
        model.model_validate(
            {
                "chunk_index": 0,
                "context_scan_trace": "Trace",
                "search_context_anchor": None,
                "extracted_facts": {
                    "fact_a": "value",
                    "extra_fact": "forbidden",
                },
            }
        )
