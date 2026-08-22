"""Unit tests for synthesis payload compression.

Tests unbounded mode, prioritized stratification, heavy key stripping, results normalization,
empty evaluation validation, and all 4 ISTQB heterogeneous payload partitions.
"""

import json
from typing import Any
from unittest.mock import patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.exceptions import AppException
from backend_v2.models.domain.synthesis import DistilledEvaluation
from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor
from backend_v2.settings import Settings


class DistilledEvaluationFactory(ModelFactory[DistilledEvaluation]):
    __model__ = DistilledEvaluation


def test_compress_synthesis_payload_strips_atom_quotes() -> None:
    """PROMISE: Prove that _compress_synthesis_payload strips evaluations and massive atom_quotes."""
    massive_string = "A" * 1000000

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

    with pytest.raises(AppException) as exc_info3:
        SynthesisPayloadCompressor.compress_synthesis_payload("   ")
    assert exc_info3.value.details["error_code"] == "VALIDATION_FAILED"


def test_compress_synthesis_payload_string_input() -> None:
    """PROMISE: Prove that _compress_synthesis_payload preserves and trims plain string payloads."""
    res = SynthesisPayloadCompressor.compress_synthesis_payload("  hello markdown world  ")
    assert res == "hello markdown world"


def test_compress_synthesis_payload_scalar_input() -> None:
    """PROMISE: Prove that _compress_synthesis_payload stringifies int, float, and bool scalars."""
    assert SynthesisPayloadCompressor.compress_synthesis_payload(42) == "42"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(3.14) == "3.14"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(True) == "True"


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


def test_compress_synthesis_payload_basemodel_input() -> None:
    """PROMISE: Prove that passing a BaseModel or a list of BaseModels handles model_dump correctly."""
    eval_mock = DistilledEvaluationFactory.build()

    # Passing single BaseModel
    res1 = SynthesisPayloadCompressor.compress_synthesis_payload(eval_mock)
    assert json.loads(res1)

    # Passing list of BaseModels and dicts
    res2 = SynthesisPayloadCompressor.compress_synthesis_payload([eval_mock, eval_mock.model_dump()])
    assert json.loads(res2)


def test_compress_synthesis_payload_negative_non_dict_evaluation() -> None:
    """PROMISE: Prove that an evaluation item not being a dict crashes."""
    payload = {"evaluations": ["not_a_dict_evaluation"]}
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Evaluation item must be a dictionary" in str(exc_info.value.message)


def test_compress_synthesis_payload_negative_missing_mandatory_field() -> None:
    """PROMISE: Prove that a missing mandatory field raises a KeyError wrapped in an AppException."""
    payload: dict[str, Any] = {"evaluations": [{"exact_quotes": []}]}  # missing atom_id
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Missing mandatory field in evaluation" in str(exc_info.value.message)


def test_compress_synthesis_payload_negative_validation_error() -> None:
    """PROMISE: Prove that a pydantic validation error raises an AppException."""
    payload: dict[str, Any] = {"evaluations": [{"atom_id": "tda_123", "exact_quotes": {"wrong": "type"}}]}

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Failed to hydrate evaluation" in str(exc_info.value.message)


def test_compress_payload_unbounded_when_zero_evaluations_limit() -> None:
    """PROMISE: Prove that when max_synthesis_evaluations == 0, all evaluations are forwarded without truncation."""
    evals = [
        {"atom_id": f"a{i}", "exact_quotes": [f"Quote for atom {i}"], "semantic_reasoning": f"Reason {i}"}
        for i in range(100)
    ]
    payload = {"evaluations": evals}

    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=0),
    ):
        compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_dict = json.loads(compressed_str)

    result_evals = compressed_dict.get("evaluations", [])
    assert len(result_evals) == 100


def test_compress_payload_prioritized_stratification_retains_critical_deficits_over_passes() -> None:
    """PROMISE: Prove that prioritized stratification retains 70% deficits and applies dynamic spillover."""
    deficits = [
        {
            "atom_id": f"def_{i}",
            "status": "FAILED",
            "exact_quotes": [f"Deficit quote long evidence {i}"],
            "semantic_reasoning": f"Failed rule {i}",
        }
        for i in range(10)
    ]
    passes = [
        {
            "atom_id": f"pass_{i}",
            "status": "PASSED",
            "exact_quotes": [f"Pass quote {i}"],
            "semantic_reasoning": f"Passed rule {i}",
        }
        for i in range(20)
    ]
    payload = {"evaluations": deficits + passes}

    # Limit of 10 -> 7 deficits (70%) and 3 passes (30%)
    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=10),
    ):
        compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_dict = json.loads(compressed_str)

    result_evals = compressed_dict.get("evaluations", [])
    assert len(result_evals) == 10

    def_count = sum(1 for e in result_evals if str(e["atom_id"]).startswith("def_"))
    pass_count = sum(1 for e in result_evals if str(e["atom_id"]).startswith("pass_"))
    assert def_count == 7
    assert pass_count == 3


def test_compress_payload_stratification_is_100_percent_deterministic_with_tiebreakers() -> None:
    """PROMISE: Prove that output evaluations are sorted canonically by atom_id for deterministic serialization."""
    evals = [
        {"atom_id": f"atom_{i:02d}", "exact_quotes": ["Evidence quote"], "semantic_reasoning": "Reason"}
        for i in reversed(range(20))
    ]
    payload = {"evaluations": evals}

    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=10),
    ):
        compressed_str_1 = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_str_2 = SynthesisPayloadCompressor.compress_synthesis_payload(payload)

    assert compressed_str_1 == compressed_str_2
    compressed_dict = json.loads(compressed_str_1)
    result_evals = compressed_dict.get("evaluations", [])
    atom_ids = [e["atom_id"] for e in result_evals]
    assert atom_ids == sorted(atom_ids)


def test_compress_payload_strips_hydrated_references_and_heavy_keys() -> None:
    """PROMISE: Prove that hydrated_references, _step_metadata, _audit_signature, and _evaluative_matrices are stripped."""
    payload: dict[str, Any] = {
        "evaluations": [{"atom_id": "a1", "exact_quotes": ["Valid quote"]}],
        "shuffled_atoms": ["atom_1", "atom_2"],
        "atom_quotes": {"blk_1": []},
        "hydrated_references": {"ref_1": "doc_content"},
        "_step_metadata": {"exec_id": "exe_123"},
        "_audit_signature": "sig_abc",
        "_evaluative_matrices": ["matrix_1"],
    }

    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    compressed_dict = json.loads(compressed_str)

    assert "shuffled_atoms" not in compressed_dict
    assert "atom_quotes" not in compressed_dict
    assert "hydrated_references" not in compressed_dict
    assert "_step_metadata" not in compressed_dict
    assert "_audit_signature" not in compressed_dict
    assert "_evaluative_matrices" not in compressed_dict
    assert "evaluations" in compressed_dict


def test_compress_payload_with_results_only_no_evaluations() -> None:
    """PROMISE: Prove that payloads containing only 'results' are normalized and filtered cleanly."""
    payload: dict[str, Any] = {
        "results": [
            {
                "atom_id": "a1",
                "exact_quotes": ["Long quote from source evidence document"],
                "semantic_reasoning": "Reasoning trace",
                "extra_bloat": "should be stripped by DistilledEvaluation",
            },
            {
                "atom_id": "a2",
                "output_text": "plain text result",
                "status": "PASSED",
                "extra_junk": "discarded",
            },
        ]
    }

    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    compressed_dict = json.loads(compressed_str)

    results = compressed_dict.get("results", [])
    assert len(results) == 2
    assert results[0]["atom_id"] == "a1"
    assert "extra_bloat" not in results[0]
    assert results[1]["atom_id"] == "a2"
    assert results[1]["output_text"] == "plain text result"
    assert "extra_junk" not in results[1]


def test_compress_payload_evaluations_empty_after_compression_fails_fast() -> None:
    """PROMISE: Prove that if all quotes are invalid/empty and evaluations becomes empty, compression raises AppException."""
    payload = {
        "evaluations": [
            {"atom_id": "a1", "exact_quotes": ["None", "null", "N/A", "N/A - insufficient data", "[bracketed]"]}
        ]
    }

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Evaluations list cannot be empty after compression" in str(exc_info.value.message)


def test_compress_payload_heterogeneous_dag_types() -> None:
    """PROMISE: Verify all 4 ISTQB heterogeneous payload partitions (dict, list, str, scalar/empty)."""
    # 1. Dict
    dict_payload = {"summary": "Executive summary text", "score": 95.5}
    dict_res = SynthesisPayloadCompressor.compress_synthesis_payload(dict_payload)
    assert json.loads(dict_res)["summary"] == "Executive summary text"

    # 2. List
    list_payload = [{"item": 1}, {"item": 2}]
    list_res = SynthesisPayloadCompressor.compress_synthesis_payload(list_payload)
    assert len(json.loads(list_res)) == 2

    # 3. String
    str_res = SynthesisPayloadCompressor.compress_synthesis_payload("   # Markdown Heading\n\nContent   ")
    assert str_res == "# Markdown Heading\n\nContent"

    # 4. Scalar and empty
    assert SynthesisPayloadCompressor.compress_synthesis_payload(100) == "100"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(99.9) == "99.9"
    assert SynthesisPayloadCompressor.compress_synthesis_payload(False) == "False"

    with pytest.raises(AppException):
        SynthesisPayloadCompressor.compress_synthesis_payload(None)  # type: ignore[arg-type]
    with pytest.raises(AppException):
        SynthesisPayloadCompressor.compress_synthesis_payload("")
    with pytest.raises(AppException):
        SynthesisPayloadCompressor.compress_synthesis_payload({})
