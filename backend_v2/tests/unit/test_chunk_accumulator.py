from typing import Any

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.orchestrator.chunk_accumulator import ChunkAccumulator


def test_chunk_accumulator_first_chunk() -> None:
    accumulator = ChunkAccumulator()
    chunk: dict[str, Any] = {
        "evaluations": [
            {
                "atom_id": "a1",
                "exact_quote": "Yes",
                "mechanical_trace": "Traced",
            },
            {
                "atom_id": "a2",
                "exact_quote": "",
                "mechanical_trace": "Traced 2",
            },
        ],
        "mechanical_trace": "A reason",
    }
    accumulator.add(chunk)
    res = accumulator.get_final_result()
    assert res["evaluations"][0]["exact_quote"] == "Yes"
    assert res["evaluations"][1]["exact_quote"] == ""
    assert res["mechanical_trace"] == "A reason"


def test_chunk_accumulator_merges_evaluations() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"evaluations": [{"atom_id": "a1", "exact_quote": "Q1", "mechanical_trace": "M1"}]}
    chunk2: dict[str, Any] = {"evaluations": [{"atom_id": "a2", "exact_quote": "", "mechanical_trace": "M2"}]}
    accumulator.add(chunk1)
    accumulator.add(chunk2)
    res = accumulator.get_final_result()["evaluations"]
    assert len(res) == 2
    assert res[0]["exact_quote"] == "Q1"
    assert res[1]["exact_quote"] == ""


def test_chunk_accumulator_dlq_on_invalid() -> None:
    accumulator = ChunkAccumulator()
    # Providing an unknown field causes Pydantic to fail and marks it as DLQ
    chunk: dict[str, Any] = {
        "evaluations": [
            {
                "atom_id": "a1",
                "exact_quote": "Q",
                "extra_field_not_allowed": "should fail",
            }
        ]
    }
    accumulator.add(chunk)
    res = accumulator.get_final_result()["evaluations"]
    assert res[0]["dlq_status"] is True


def test_chunk_accumulator_merges_string_traces() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"mechanical_trace": "First chunk logic.", "evaluation_notes": "Note 1"}
    chunk2: dict[str, Any] = {"mechanical_trace": "Second chunk logic.", "evaluation_notes": "Note 2"}
    accumulator.add(chunk1)
    accumulator.add(chunk2)

    result = accumulator.get_final_result()
    assert result["mechanical_trace"] == "First chunk logic.\n\n[Chunk]: Second chunk logic."
    assert result["evaluation_notes"] == "Note 1\n\n[Chunk]: Note 2"


def test_chunk_accumulator_merges_nested_xai_extensions() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"matrix_toulmin": {"falsification": "Claim is weak.", "citations": ["doc1"]}}
    chunk2: dict[str, Any] = {"matrix_toulmin": {"falsification": "And contradicts itself.", "citations": ["doc2"]}}
    accumulator.add(chunk1)
    accumulator.add(chunk2)

    result = accumulator.get_final_result()
    assert result["matrix_toulmin"]["falsification"] == "Claim is weak. And contradicts itself."
    assert result["matrix_toulmin"]["citations"] == ["doc1", "doc2"]


def test_chunk_accumulator_fails_fast_on_incompatible_types() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"matrix_test": {"key": "string value"}}
    chunk2: dict[str, Any] = {"matrix_test": {"key": 123}}  # Incompatible integer type

    accumulator.add(chunk1)

    with pytest.raises(AppException) as excinfo:
        accumulator.add(chunk2)

    assert excinfo.value.status_code == 500
    assert "Strict Fail-Fast: Unresolvable key collision" in excinfo.value.message


def test_chunk_accumulator_handles_missing_keys_gracefully() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"matrix_1": {"data": "A"}}
    chunk2: dict[str, Any] = {"matrix_2": {"data": "B"}}

    accumulator.add(chunk1)
    accumulator.add(chunk2)

    result = accumulator.get_final_result()
    assert result["matrix_1"]["data"] == "A"
    assert result["matrix_2"]["data"] == "B"
