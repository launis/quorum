"""Unit tests for RenderedSynthesisCache Pydantic V2 validation and hydration."""

import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import RenderedSynthesisCache
from backend_v2.models.view.sdui import ParagraphBlock


def test_rendered_synthesis_cache_hydration_fails_with_extra() -> None:
    """Verify that RenderedSynthesisCache strictly forbids extra fields."""
    synthesis_payload = {
        "evaluation_notes": "Tekoäly tuotti kattavan...",
        "reasoning_trace": "My reasoning process...",
        "extracted_facts": {},
        "_step_metadata": {"token_usage": {}},
    }

    with pytest.raises(ValidationError) as exc_info:
        RenderedSynthesisCache.model_validate(synthesis_payload)

    assert "extra_forbidden" in str(exc_info.value) or "Extra inputs are not permitted" in str(exc_info.value)
    assert "evaluation_notes" in str(exc_info.value)


def test_rendered_synthesis_cache_valid_hydration() -> None:
    """Verify clean Pydantic V2 discriminated union hydration for RenderedSynthesisCache."""
    block = ParagraphBlock(text="Analyysin sisältö...", exact_quotes=[], citations=[])
    valid_payload = {
        "section_syntheses": {"blk_34def5d628ba4ed4": [block]},
        "row_explanations": {"mat_12345678": "Explanation text"},
        "row_curated_quotes": {},
        "cited_sources": ["Doc 1"],
    }

    cache = RenderedSynthesisCache.model_validate(valid_payload)
    assert cache is not None
    assert "blk_34def5d628ba4ed4" in cache.section_syntheses
    first_block = cache.section_syntheses["blk_34def5d628ba4ed4"][0]
    assert isinstance(first_block, ParagraphBlock)
    assert first_block.text == "Analyysin sisältö..."


def test_rendered_synthesis_cache_serialization_roundtrip() -> None:
    """Verify JSON serialization round-trip preservation."""
    block = ParagraphBlock(text="Roundtrip text", exact_quotes=[], citations=[])
    cache = RenderedSynthesisCache(
        section_syntheses={"layout_1": [block]},
        row_explanations={"m1": "Expl"},
    )
    raw_json = cache.model_dump_json()
    rehydrated = RenderedSynthesisCache.model_validate_json(raw_json)
    rehydrated_block = rehydrated.section_syntheses["layout_1"][0]
    assert isinstance(rehydrated_block, ParagraphBlock)
    assert rehydrated_block.text == "Roundtrip text"
