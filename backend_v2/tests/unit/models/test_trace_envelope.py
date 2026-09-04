"""Unit tests for TraceEventMetadataEnvelope ISTQB equivalence partitions.

Validates polymorphic envelope extraction of step metadata from trace event content.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataEnvelope


def test_partition_1_polymorphic_sdui_block_with_step_metadata() -> None:
    """Validate extraction of _step_metadata alongside arbitrary SDUI block fields."""
    payload: dict[str, Any] = {
        "id": "blk_hero_123",
        "block_type": "hero_insight",
        "text": "Key executive finding.",
        "_audit_signature": "sig_abc456",
        "_step_metadata": {
            "step_id": "stp_evaluate",
            "model_strategy": "fast",
            "chunk_size": 2,
        },
    }

    envelope = TraceEventMetadataEnvelope.model_validate(payload)
    assert envelope.step_metadata is not None
    assert isinstance(envelope.step_metadata, StepTraceMetadataDTO)
    assert envelope.step_metadata.step_id == "stp_evaluate"
    assert envelope.step_metadata.model_strategy == "fast"
    assert envelope.step_metadata.chunk_size == 2


def test_partition_2_missing_step_metadata() -> None:
    """Validate that payload without _step_metadata returns None without raising."""
    payload: dict[str, Any] = {
        "id": "blk_plain_789",
        "block_type": "text_block",
        "content": "Simple message.",
    }

    envelope = TraceEventMetadataEnvelope.model_validate(payload)
    assert envelope.step_metadata is None


def test_partition_3_malformed_step_metadata_fails() -> None:
    """Validate that malformed _step_metadata triggers Pydantic ValidationError."""
    payload: dict[str, Any] = {
        "id": "blk_invalid",
        "_step_metadata": "not_a_valid_dictionary_or_model",
    }

    with pytest.raises(ValidationError):
        TraceEventMetadataEnvelope.model_validate(payload)


def test_partition_4_token_usage_telemetry_extraction() -> None:
    """Validate detailed TokenUsage extraction within StepTraceMetadataDTO."""
    payload: dict[str, Any] = {
        "block_id": "blk_scorecard_01",
        "_step_metadata": {
            "step_id": "stp_matrix_audit",
            "model_strategy": "reasoning",
            "physical_model": "vertex_ai/gemini-2.5-flash",
            "system_fingerprint": "fp_2026_weights",
            "token_usage": {
                "prompt_tokens": 1500,
                "completion_tokens": 350,
                "total_tokens": 1850,
                "cached_tokens": 1000,
                "reasoning_tokens": 120,
                "cost_usd": 0.0042,
            },
        },
    }

    envelope = TraceEventMetadataEnvelope.model_validate(payload)
    assert envelope.step_metadata is not None
    assert envelope.step_metadata.token_usage is not None
    assert isinstance(envelope.step_metadata.token_usage, TokenUsage)
    assert envelope.step_metadata.token_usage.prompt_tokens == 1500
    assert envelope.step_metadata.token_usage.completion_tokens == 350
    assert envelope.step_metadata.token_usage.cached_tokens == 1000
    assert envelope.step_metadata.token_usage.reasoning_tokens == 120
    assert envelope.step_metadata.token_usage.cost_usd == pytest.approx(0.0042)
