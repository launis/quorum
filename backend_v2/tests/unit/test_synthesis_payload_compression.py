import json
from typing import Any

from polyfactory.factories.pydantic_factory import ModelFactory

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
    """PROMISE: Prove that _compress_synthesis_payload handles empty/missing inputs safely."""
    compressed_empty_dict = SynthesisPayloadCompressor.compress_synthesis_payload({})
    compressed_empty_list = SynthesisPayloadCompressor.compress_synthesis_payload([])

    assert compressed_empty_dict == "{}"
    assert compressed_empty_list == "[]"


def test_compress_synthesis_payload_negative_invalid_types() -> None:
    """PROMISE: Prove that _compress_synthesis_payload does not crash on invalid payload structures."""
    payload: dict[str, Any] = {
        "evaluations": "This should be a list, not a string",
        "atom_quotes": 12345,
        "shuffled_atoms": {"wrong": "type"},
        "nested": {"atom_quotes": None, "evaluations": {"invalid": "dict instead of list"}},
    }

    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    compressed_dict = json.loads(compressed_str)

    assert compressed_dict.get("evaluations") is None
    assert "atom_quotes" not in compressed_dict
    assert "shuffled_atoms" not in compressed_dict

    nested = compressed_dict.get("nested", {})
    assert "atom_quotes" not in nested
    assert nested.get("evaluations") is None
