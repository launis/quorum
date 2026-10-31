"""Unit tests for SynthesisPayloadCompressor (SSOT).

Tests unbounded mode, prioritized stratification, heavy key stripping, results normalization,
empty evaluation validation, and all 4 ISTQB heterogeneous payload partitions.
"""

import json
from unittest.mock import patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import JsonValue, ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.synthesis import DistilledEvaluation
from backend_v2.models.dtos.atom_result import AtomResultDTO, EvaluatedAtomDTO, HydratedAtomDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor
from backend_v2.settings import Settings


class DistilledEvaluationFactory(ModelFactory[DistilledEvaluation]):
    __model__ = DistilledEvaluation
    atom_id = "tda_default_atom"


def test_compress_synthesis_payload_strips_atom_quotes() -> None:
    """PROMISE: Prove that _compress_synthesis_payload strips atom_quotes, preserves unbounded by default, and slices when positive limits are configured."""
    massive_string = "A" * 1000

    eval_mock = DistilledEvaluationFactory.build(
        atom_id="tda_123",
        exact_quotes=[massive_string],
        semantic_reasoning=massive_string,
    )

    payload: dict[str, JsonValue] = {
        "results": [eval_mock.model_dump()],
        "atom_quotes": {"blk_123": [{"level": 5, "level_name": "High", "quote": massive_string}]},
    }

    # Default unbounded settings (max_synthesis_quote_length=0, max_synthesis_reasoning_length=0)
    compressed_unbounded = json.loads(SynthesisPayloadCompressor.compress_synthesis_payload(payload))
    assert "atom_quotes" not in compressed_unbounded
    assert len(compressed_unbounded["results"][0]["exact_quotes"][0]) == 1000
    assert len(compressed_unbounded["results"][0]["semantic_reasoning"]) == 1000

    # Explicit positive bounds slice quotes and reasoning
    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_quote_length=300, max_synthesis_reasoning_length=300),
    ):
        compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_dict = json.loads(compressed_str)

    pruned_evals = compressed_dict["results"]
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
    payload: dict[str, JsonValue] = {
        "results": "This should be a list, not a string",
        "atom_quotes": 12345,
        "shuffled_atoms": {"wrong": "type"},
        "nested": {"atom_quotes": None, "results": {"invalid": "dict instead of list"}},
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
    payload = {"results": ["not_a_dict_evaluation"]}
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Evaluation item must be a dictionary" in str(exc_info.value.message)


def test_compress_synthesis_payload_negative_missing_mandatory_field() -> None:
    """PROMISE: Prove that a missing mandatory field raises a KeyError wrapped in an AppException."""
    payload: dict[str, JsonValue] = {"results": [{"exact_quotes": []}]}  # missing atom_id
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Missing mandatory field in evaluation" in str(exc_info.value.message)


def test_compress_synthesis_payload_negative_validation_error() -> None:
    """PROMISE: Prove that a pydantic validation error raises an AppException."""
    payload: dict[str, JsonValue] = {"results": [{"atom_id": "tda_123", "exact_quotes": {"wrong": "type"}}]}

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
    payload = {"results": evals}

    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=0),
    ):
        compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_dict = json.loads(compressed_str)

    result_evals = compressed_dict["results"]
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
    payload = {"results": deficits + passes}

    # Limit of 10 -> 7 deficits (70%) and 3 passes (30%)
    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=10),
    ):
        compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_dict = json.loads(compressed_str)

    result_evals = compressed_dict["results"]
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
    payload = {"results": evals}

    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=10),
    ):
        compressed_str_1 = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_str_2 = SynthesisPayloadCompressor.compress_synthesis_payload(payload)

    assert compressed_str_1 == compressed_str_2
    compressed_dict = json.loads(compressed_str_1)
    result_evals = compressed_dict["results"]
    atom_ids = [e["atom_id"] for e in result_evals]
    assert atom_ids == sorted(atom_ids)


def test_compress_payload_strips_hydrated_references_and_heavy_keys() -> None:
    """PROMISE: Prove that hydrated_references, _step_metadata, _audit_signature, and _evaluative_matrices are stripped."""
    payload: dict[str, JsonValue] = {
        "results": [{"atom_id": "a1", "exact_quotes": ["Valid quote"]}],
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
    assert "results" in compressed_dict


def test_compress_payload_evaluations_empty_after_compression_fails_fast() -> None:
    """PROMISE: Prove that if all quotes are invalid/empty and results becomes empty, compression raises AppException."""
    payload = {
        "results": [
            {"atom_id": "a1", "exact_quotes": ["None", "null", "N/A", "N/A - insufficient data", "[bracketed]"]}
        ]
    }

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Results list cannot be empty after compression" in str(exc_info.value.message)


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
        SynthesisPayloadCompressor.compress_synthesis_payload(None)
    with pytest.raises(AppException):
        SynthesisPayloadCompressor.compress_synthesis_payload("")
    with pytest.raises(AppException):
        SynthesisPayloadCompressor.compress_synthesis_payload({})


def test_compress_payload_non_dict_list_unsupported_type_fails_fast() -> None:
    """PROMISE: Prove that unsupported types that cannot be converted to dict/list/str raise AppException."""

    class CustomObject:
        pass

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(CustomObject())
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_compress_payload_results_without_exact_quotes_uses_normalizer() -> None:
    """PROMISE: Prove that result items without exact_quotes or with exact_quotes normalization are processed."""
    payload = {
        "results": [
            {
                "output_text": "Processed text",
                "status": "PASSED",
                "atom_id": "tda_atom_1",
                "extra_key": "should_be_stripped",
            },
            {
                "exact_quotes": ["Valid quote for distillation"],
                "atom_id": "tda_atom_2",
                "semantic_reasoning": "Reason text",
                "extensions": {"status": "PASSED"},
            },
            {
                "exact_quotes": ["Valid quote 3"],
                "atom_id": "tda_atom_3",
                "status": "PASSED",
            },
        ]
    }

    res_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    res_dict = json.loads(res_str)
    assert len(res_dict["results"]) == 3
    assert res_dict["results"][0]["atom_id"] == "tda_atom_1"
    assert res_dict["results"][0]["status"] == "PASSED"
    assert res_dict["results"][0]["semantic_reasoning"] == "Processed text"
    assert "extra_key" not in res_dict["results"][0]


def test_compress_payload_nested_list_of_results() -> None:
    """PROMISE: Prove that nested list structures are properly traversed and stripped."""
    payload = {
        "step_output": [
            {
                "results": [
                    {"atom_id": "tda_1", "exact_quotes": ["Quote 1"]},
                ],
                "hydrated_references": {"ref": "value"},
            }
        ]
    }
    res_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    res_dict = json.loads(res_str)
    assert "hydrated_references" not in res_dict["step_output"][0]
    assert len(res_dict["step_output"][0]["results"]) == 1


def test_compress_payload_with_evaluated_atom_dtos() -> None:
    """PROMISE: Prove that EvaluatedAtomDTO objects are properly sanitized, stratified, and compressed."""
    dto1 = EvaluatedAtomDTO(
        tda_id="tda_failed_1",
        atom_id="tda_failed_1",
        status="FAILED",
        exact_quotes=["Failed evidence quote 1"],
        evaluation_reasoning="Reasoning for failure",
    )
    dto2 = EvaluatedAtomDTO(
        tda_id="tda_passed_1",
        atom_id="tda_passed_1",
        status="PASSED",
        exact_quotes=["Passed evidence quote 1"],
        evaluation_reasoning="Reasoning for pass",
    )
    payload = {"results": [dto1, dto2]}

    res_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    res_dict = json.loads(res_str)
    assert len(res_dict["results"]) == 2
    atom_ids = [r["atom_id"] for r in res_dict["results"]]
    assert "tda_failed_1" in atom_ids
    assert "tda_passed_1" in atom_ids


def test_compress_payload_stratification_dynamic_spillover_small_strengths() -> None:
    """PROMISE: Prove dynamic spillover when strengths partition is smaller than allocated budget."""
    deficits = [
        EvaluatedAtomDTO(
            tda_id=f"tda_def_{i:02d}",
            atom_id=f"tda_def_{i:02d}",
            status="FAILED",
            exact_quotes=[f"Quote def {i}"],
            evaluation_reasoning="Deficit reasoning",
        )
        for i in range(15)
    ]
    strengths = [
        EvaluatedAtomDTO(
            tda_id="tda_str_01",
            atom_id="tda_str_01",
            status="PASSED",
            exact_quotes=["Quote str 1"],
            evaluation_reasoning="Strength reasoning",
        )
    ]
    payload = {"results": deficits + strengths}

    # Limit = 10 (deficit_budget = 7, strength_budget = 3, but strengths has only 1, so deficits gets 9)
    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=10),
    ):
        res_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        res_dict = json.loads(res_str)
        assert len(res_dict["results"]) == 10
        # 1 strength and 9 deficits
        assert any(r["atom_id"] == "tda_str_01" for r in res_dict["results"])
        retained_deficits = [r for r in res_dict["results"] if r["atom_id"] != "tda_str_01"]
        assert len(retained_deficits) == 9


def test_compress_payload_invalid_evaluation_item_type() -> None:
    """PROMISE: Prove that non-dict non-EvaluatedAtomDTO items in results raise AppException."""
    payload = {"results": ["not_a_valid_evaluation_item"]}
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_compress_synthesis_payload_with_hydrated_atom_dto_dict() -> None:
    """PROMISE: Prove that a dictionary mapping atom IDs to HydratedAtomDTO objects compresses without error."""
    atom_dto = HydratedAtomDTO(
        sdui_component="boolean_card",
        resolved_claim="Claim text for atom 1",
        source_quotes=("Verbatim quote",),
    )
    payload: dict[str, HydratedAtomDTO] = {
        "tda_0195f3a00000700081b1d71000000001": atom_dto,
    }
    res_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    res_dict = json.loads(res_str)
    assert "tda_0195f3a00000700081b1d71000000001" in res_dict
    assert res_dict["tda_0195f3a00000700081b1d71000000001"]["resolved_claim"] == "Claim text for atom 1"


def test_compress_payload_matrix_payload_dto_with_empty_results_fails_fast() -> None:
    """PROMISE: Prove that passing an empty results list triggers AppException with VALIDATION_FAILED."""
    payload = {"results": []}
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_compress_payload_results_item_missing_atom_id_fails_fast() -> None:
    """PROMISE: Prove that an evaluation item missing an atom_id triggers AppException with VALIDATION_FAILED."""
    payload = {"results": [{"exact_quotes": ["valid quote"], "status": "PASSED"}]}
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_clean_and_distill_payload_retains_failed_and_na_without_quotes_or_character_slicing() -> None:
    """Verify FAILED and N_A evaluations without quotes retain full 1800-char 4-step Micro-CoT reasoning and topological lineage."""
    micro_cot_1800 = (
        "1. step_1_identify_premise: Anchor premise identified in section 2.\n"
        "2. step_2_literal_scan: Performed literal scan across source segments.\n"
        + ("Detailed forensic scan notes. " * 55)
        + "\n3. step_3_evaluate_anti_patterns: Explicit anti-pattern rubric failure confirmed.\n"
        "4. step_4_final_conclusion: Assertion fails due to missing quantitative governance threshold."
    )
    assert len(micro_cot_1800) >= 1800

    failed_dto = EvaluatedAtomDTO(
        tda_id="tda_parent",
        atom_id="tda_parent",
        status=ExecutionStatus.FAILED,
        exact_quotes=[],
        evaluation_reasoning=micro_cot_1800,
    )
    na_atom = AtomResultDTO(
        tda_id="tda_child",
        status=ExecutionStatus.N_A,
        evaluation_reasoning=micro_cot_1800,
        depends_on_tda_ids=["tda_parent"],
        short_circuit_reason_tda_ids=["tda_parent"],
    )

    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload({"results": [failed_dto, na_atom]})
    compressed_dict = json.loads(compressed_str)
    results = compressed_dict["results"]
    assert len(results) == 2

    parent_res = next(r for r in results if r["atom_id"] == "tda_parent")
    child_res = next(r for r in results if r["atom_id"] == "tda_child")

    assert parent_res["semantic_reasoning"] == micro_cot_1800
    assert "step_3_evaluate_anti_patterns" in parent_res["semantic_reasoning"]
    assert "step_4_final_conclusion" in parent_res["semantic_reasoning"]
    assert parent_res["topological_out_degree"] == 1

    assert child_res["semantic_reasoning"] == micro_cot_1800
    assert child_res["short_circuit_reason_tda_ids"] == ["tda_parent"]
    assert child_res["depends_on_tda_ids"] == ["tda_parent"]


def test_clean_and_distill_payload_explicit_positive_bound_slices_at_boundary() -> None:
    """ISTQB BVA: Verify evaluation_reasoning lengths 1499, 1500, and 1501 when max_synthesis_reasoning_length=1500."""
    dto_1499 = EvaluatedAtomDTO(
        tda_id="tda_1499",
        atom_id="tda_1499",
        status=ExecutionStatus.FAILED,
        exact_quotes=[],
        evaluation_reasoning="A" * 1499,
    )
    dto_1500 = EvaluatedAtomDTO(
        tda_id="tda_1500",
        atom_id="tda_1500",
        status=ExecutionStatus.FAILED,
        exact_quotes=[],
        evaluation_reasoning="B" * 1500,
    )
    dto_1501 = EvaluatedAtomDTO(
        tda_id="tda_1501",
        atom_id="tda_1501",
        status=ExecutionStatus.FAILED,
        exact_quotes=[],
        evaluation_reasoning="C" * 1501,
    )

    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_reasoning_length=1500),
    ):
        compressed_dict = json.loads(
            SynthesisPayloadCompressor.compress_synthesis_payload({"results": [dto_1499, dto_1500, dto_1501]})
        )

    by_id = {r["atom_id"]: r["semantic_reasoning"] for r in compressed_dict["results"]}
    assert len(by_id["tda_1499"]) == 1499
    assert len(by_id["tda_1500"]) == 1500
    assert len(by_id["tda_1501"]) == 1500
    assert by_id["tda_1501"] == "C" * 1500


def test_clean_and_distill_payload_drops_passed_atom_with_empty_quotes_and_no_reasoning() -> None:
    """Negative test: PASSED atom with empty quotes, no reasoning, and is_inverse_evidence=False is dropped."""
    empty_passed = EvaluatedAtomDTO(
        tda_id="tda_empty_pass",
        atom_id="tda_empty_pass",
        status=ExecutionStatus.PASSED,
        exact_quotes=[],
        evaluation_reasoning=None,
        is_inverse_evidence=False,
    )
    valid_failed = EvaluatedAtomDTO(
        tda_id="tda_valid_fail",
        atom_id="tda_valid_fail",
        status=ExecutionStatus.FAILED,
        exact_quotes=[],
        evaluation_reasoning="Failed due to missing evidence.",
    )
    compressed_dict = json.loads(
        SynthesisPayloadCompressor.compress_synthesis_payload({"results": [empty_passed, valid_failed]})
    )
    atom_ids = [r["atom_id"] for r in compressed_dict["results"]]
    assert "tda_empty_pass" not in atom_ids
    assert atom_ids == ["tda_valid_fail"]


def test_prune_and_stratify_evaluations_prioritizes_inverse_evidence_and_out_degree_when_limit_positive() -> None:
    """Verify deficit priority sorting places inverse evidence first, highest out_degree second, and includes N_A."""
    eval_a0 = DistilledEvaluation(
        atom_id="a0",
        status="FAILED",
        semantic_reasoning="Alphabetical leaf failure",
        topological_out_degree=0,
        is_inverse_evidence=False,
    )
    eval_z9 = DistilledEvaluation(
        atom_id="z9",
        status="FAILED",
        semantic_reasoning="Root causal blocker",
        topological_out_degree=4,
        is_inverse_evidence=False,
    )
    eval_n1 = DistilledEvaluation(
        atom_id="n1",
        status="N_A",
        semantic_reasoning="Short-circuited child",
        short_circuit_reason_tda_ids=["z9"],
        topological_out_degree=0,
        is_inverse_evidence=False,
    )
    eval_m5 = DistilledEvaluation(
        atom_id="m5",
        status="FAILED",
        semantic_reasoning="Poison anti-pattern hit",
        topological_out_degree=1,
        is_inverse_evidence=True,
    )

    # Under limit=2 (with all 4 items in deficits and 0 strengths), only top 2 priority deficits survive: m5 and z9
    top_two = SynthesisPayloadCompressor._prune_and_stratify_evaluations(
        [eval_a0, eval_z9, eval_n1, eval_m5],
        limit=2,
    )
    assert {e.atom_id for e in top_two} == {"m5", "z9"}

    # Under limit=3, top 3 priority deficits survive: m5 (inverse=True), z9 (out_degree=4), a0 (short_circuit_len=0)
    top_three = SynthesisPayloadCompressor._prune_and_stratify_evaluations(
        [eval_a0, eval_z9, eval_n1, eval_m5],
        limit=3,
    )
    assert {e.atom_id for e in top_three} == {"m5", "z9", "a0"}

    # Under limit=4, n1 is also retained in deficits
    all_four = SynthesisPayloadCompressor._prune_and_stratify_evaluations(
        [eval_a0, eval_z9, eval_n1, eval_m5],
        limit=4,
    )
    assert {e.atom_id for e in all_four} == {"a0", "m5", "n1", "z9"}


def test_distilled_evaluation_extra_field_raises_validation_error() -> None:
    """Error-path test: DistilledEvaluation.model_validate rejects unpermitted extra keys (extra='forbid')."""
    with pytest.raises(ValidationError):
        DistilledEvaluation.model_validate(
            {
                "atom_id": "tda_0195f3a0000070008000000000000001",
                "status": "FAILED",
                "unpermitted_extra_key": "forbidden",
            }
        )
