from typing import Any

from backend_v2.services.orchestrator.chunk_accumulator import ChunkAccumulator


def test_chunk_accumulator_first_chunk() -> None:
    accumulator = ChunkAccumulator()
    chunk: dict[str, Any] = {"evaluations": [True, False], "reasoning_trace": "A reason"}
    accumulator.add(chunk)
    assert accumulator.get_final_result() == chunk


def test_chunk_accumulator_merges_evaluations() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"evaluations": [True]}
    chunk2: dict[str, Any] = {"evaluations": [False]}
    accumulator.add(chunk1)
    accumulator.add(chunk2)
    assert accumulator.get_final_result()["evaluations"] == [True, False]


def test_chunk_accumulator_merges_string_traces() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"reasoning_trace": "First chunk logic.", "evaluation_notes": "Note 1"}
    chunk2: dict[str, Any] = {"reasoning_trace": "Second chunk logic.", "evaluation_notes": "Note 2"}
    accumulator.add(chunk1)
    accumulator.add(chunk2)

    result = accumulator.get_final_result()
    assert result["reasoning_trace"] == "First chunk logic.\n\n[Chunk]: Second chunk logic."
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


def test_chunk_accumulator_skips_incompatible_types() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"matrix_test": {"key": "string value"}}
    chunk2: dict[str, Any] = {"matrix_test": {"key": 123}}  # Incompatible integer type

    accumulator.add(chunk1)
    accumulator.add(chunk2)

    # Should safely skip merging the integer into the string, keeping the original
    result = accumulator.get_final_result()
    assert result["matrix_test"]["key"] == "string value"


def test_chunk_accumulator_handles_missing_keys_gracefully() -> None:
    accumulator = ChunkAccumulator()
    chunk1: dict[str, Any] = {"matrix_1": {"data": "A"}}
    chunk2: dict[str, Any] = {"matrix_2": {"data": "B"}}

    accumulator.add(chunk1)
    accumulator.add(chunk2)

    result = accumulator.get_final_result()
    assert result["matrix_1"]["data"] == "A"
    assert result["matrix_2"]["data"] == "B"
