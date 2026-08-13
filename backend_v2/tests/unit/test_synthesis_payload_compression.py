import json
from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.exceptions import AppException
from backend_v2.models.domain.synthesis import DistilledEvaluation
from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor


class DistilledEvaluationFactory(ModelFactory[DistilledEvaluation]):
    __model__ = DistilledEvaluation


def test_compress_synthesis_payload_strips_atom_quotes() -> None:
    """PROMISE: Prove that _compress_synthesis_payload strips evaluations and massive atom_quotes."""
    massive_string = "A" * 1000000

    # Build evaluation using polyfactory
    eval_mock = DistilledEvaluationFactory.build(exact_quotes=[massive_string], semantic_reasoning=massive_string)

    payload: dict[str, Any] = {
        "evaluations": [eval_mock.model_dump()],
        "atom_quotes": {"blk_123": [{"level": 5, "level_name": "High", "quote": massive_string}]},
    }

    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    compressed_dict = json.loads(compressed_str)

    pruned_evals = compressed_dict.get("evaluations", [])
    assert len(pruned_evals) == 1
    assert len(pruned_evals[0]["exact_quotes"][0]) <= 300
    assert len(pruned_evals[0]["semantic_reasoning"]) <= 300

    assert len(compressed_str) < 5000


def test_compress_synthesis_payload_negative_empty_input() -> None:
    """PROMISE: Prove that _compress_synthesis_payload crashes on empty inputs (anti-happy-path)."""
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload({})
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"

    with pytest.raises(AppException) as exc_info2:
        SynthesisPayloadCompressor.compress_synthesis_payload([])
    assert exc_info2.value.details["error_code"] == "VALIDATION_FAILED"


def test_compress_synthesis_payload_negative_invalid_types() -> None:
    """PROMISE: Prove that _compress_synthesis_payload crashes on invalid payload structures (anti-happy-path)."""
    payload: dict[str, Any] = {
        "evaluations": "This should be a list, not a string",
        "atom_quotes": 12345,
        "shuffled_atoms": {"wrong": "type"},
        "nested": {"atom_quotes": None, "evaluations": {"invalid": "dict instead of list"}},
    }

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
