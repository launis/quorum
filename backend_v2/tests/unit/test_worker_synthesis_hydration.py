from unittest.mock import AsyncMock
import json
from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import RenderedSynthesisCache


def test_rendered_synthesis_cache_hydration_fails_with_extra() -> None:
    # Simulate the raw output from SynthesisDistiller / LLM
    synthesis_payload = {
        "evaluation_notes": "Tekoäly tuotti kattavan...",
        "reasoning_trace": "My reasoning process...",
        "blk_34def5d628ba4ed4": json.dumps(
            {"section_syntheses": [{"block_id": "blk_34def5d628ba4ed4", "content": "Analyysin sisältö..."}]}
        ),
        "extracted_facts": {},
        "_step_metadata": {"token_usage": {}},
    }

    delta = dict(synthesis_payload)
    delta["row_explanations"] = {}
    delta["row_curated_quotes"] = {}

    with pytest.raises(ValidationError) as exc_info:
        RenderedSynthesisCache.model_validate(delta)

    assert "Extra inputs are not permitted" in str(exc_info.value)
    assert "evaluation_notes" in str(exc_info.value)


def test_rendered_synthesis_cache_hydration_success_after_fix() -> None:
    # Simulate the raw output from SynthesisDistiller / LLM
    synthesis_payload = {
        "evaluation_notes": "Tekoäly tuotti kattavan...",
        "reasoning_trace": "My reasoning process...",
        "blk_34def5d628ba4ed4": json.dumps(
            {"section_syntheses": [{"block_id": "blk_34def5d628ba4ed4", "content": "Analyysin sisältö..."}]}
        ),
        "extracted_facts": {},
        "_step_metadata": {"token_usage": {}},
    }

    delta = dict(synthesis_payload)

    # --- PROPOSED FIX LOGIC ---
    clean_delta: dict[str, Any] = {}
    clean_delta["section_syntheses"] = delta.get("section_syntheses", {})

    for key, value in delta.items():
        if key.startswith("blk_") and isinstance(value, str):
            try:
                parsed = json.loads(value)
                if "section_syntheses" in parsed:
                    clean_delta["section_syntheses"][key] = parsed["section_syntheses"]
                elif isinstance(parsed, list):
                    clean_delta["section_syntheses"][key] = parsed
            except Exception:
                pass
        elif key.startswith("blk_") and isinstance(value, dict):
            if "section_syntheses" in value:
                clean_delta["section_syntheses"][key] = value["section_syntheses"]
            else:
                pass
        elif key.startswith("blk_") and isinstance(value, list):
            clean_delta["section_syntheses"][key] = value
        elif key in RenderedSynthesisCache.model_fields and key != "section_syntheses":
            clean_delta[key] = value

    clean_delta["row_explanations"] = {}
    clean_delta["row_curated_quotes"] = {}
    # -------------------------

    cache = RenderedSynthesisCache.model_validate(clean_delta)
    assert cache is not None
    assert "blk_34def5d628ba4ed4" in cache.section_syntheses
    assert cache.section_syntheses["blk_34def5d628ba4ed4"][0]["content"] == "Analyysin sisältö..."
