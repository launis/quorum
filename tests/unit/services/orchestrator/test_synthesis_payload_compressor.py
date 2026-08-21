"""Regression unit test for SynthesisPayloadCompressor payload size and heavy key pruning."""

import json

import pytest

from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor
from backend_v2.settings import get_settings


def test_synthesis_payload_compressor_strips_hydrated_references_and_bounds_results() -> None:
    """Test that SynthesisPayloadCompressor strips hydrated_references and bounds results to max_synthesis_evaluations."""
    settings = get_settings()

    # Simulate an extracted atom output payload (such as Step 1 Input Processing)
    many_results = [
        {
            "tda_id": f"tda_{i}",
            "matrix_id": None,
            "status": "PASSED",
            "extracted_data": None,
            "source_quote": f"This is a very long verbatim source quote number {i} from the input documents " * 5,
            "contextual_override": False,
            "evaluation_reasoning": f"Detailed reasoning trace for atom {i} with extensive text",
            "extensions": {"coaching": f"Coaching tip {i}"},
        }
        for i in range(100)
    ]

    heavy_payload = {
        "results": many_results,
        "hydrated_references": {f"tda_{i}": "Full raw page text " * 500 for i in range(100)},
        "_step_metadata": {"debug": True},
        "_audit_signature": "sig_123",
    }

    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(heavy_payload)
    compressed_dict = json.loads(compressed_str)

    # 1. hydrated_references MUST be stripped
    assert "hydrated_references" not in compressed_dict, "hydrated_references must be stripped from synthesis payload"
    assert "_step_metadata" not in compressed_dict, "_step_metadata must be stripped from synthesis payload"
    assert "_audit_signature" not in compressed_dict, "_audit_signature must be stripped from synthesis payload"

    # 2. results list MUST be compressed and bounded to max_synthesis_evaluations
    assert len(compressed_dict["results"]) <= settings.max_synthesis_evaluations, (
        f"results list must not exceed {settings.max_synthesis_evaluations} items"
    )
