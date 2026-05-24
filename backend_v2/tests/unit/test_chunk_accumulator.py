"""Unit tests for the refactored EPIC 56 ChunkAccumulator Reducer logic."""

from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException
from backend_v2.services.orchestrator.chunk_accumulator import ChunkAccumulator


class MockResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    chunk_index: int
    extracted_facts: dict[str, str | None] = Field(default_factory=dict)
    mechanical_trace: str = ""
    evaluation_notes: str = ""


def test_chunk_accumulator_reducer_deterministic_sorting() -> None:
    """Verify that chunks are sorted chronologically by chunk_index during reduction."""
    accumulator = ChunkAccumulator(response_model=MockResponseSchema)

    chunk_2: dict[str, Any] = {
        "chunk_index": 2,
        "mechanical_trace": "Trace 3",
        "evaluation_notes": "Note 3",
        "extracted_facts": {"fact_a": "Value C"},
    }
    chunk_0: dict[str, Any] = {
        "chunk_index": 0,
        "mechanical_trace": "Trace 1",
        "evaluation_notes": "Note 1",
        "extracted_facts": {"fact_a": "Value A"},
    }
    chunk_1: dict[str, Any] = {
        "chunk_index": 1,
        "mechanical_trace": "Trace 2",
        "evaluation_notes": "Note 2",
        "extracted_facts": {"fact_a": "Value B"},
    }

    # Add chunks out of chronological order
    accumulator.add(chunk_2)
    accumulator.add(chunk_0)
    accumulator.add(chunk_1)

    result = accumulator.get_final_result()

    # Traces must be concatenated in chronological order: 0 -> 1 -> 2
    assert result["mechanical_trace"] == "Trace 1\n\n[Chunk]: Trace 2\n\n[Chunk]: Trace 3"
    assert result["evaluation_notes"] == "Note 1\n\n[Chunk]: Note 2\n\n[Chunk]: Note 3"


def test_chunk_accumulator_reducer_first_wins() -> None:
    """Verify the 'First-Wins' strategy for extracted facts merging."""
    accumulator = ChunkAccumulator(response_model=MockResponseSchema)

    # fact_a is present in chunk 0.
    # fact_b is None in chunk 0, present in chunk 1, present in chunk 2. (Chunk 1 should win).
    # fact_c is "" in chunk 0, None in chunk 1, present in chunk 2. (Chunk 2 should win).
    chunk_0: dict[str, Any] = {
        "chunk_index": 0,
        "extracted_facts": {
            "fact_a": "First Fact A",
            "fact_b": None,
            "fact_c": "",
        },
    }
    chunk_1: dict[str, Any] = {
        "chunk_index": 1,
        "extracted_facts": {
            "fact_a": "Second Fact A",
            "fact_b": "First Fact B",
            "fact_c": None,
        },
    }
    chunk_2: dict[str, Any] = {
        "chunk_index": 2,
        "extracted_facts": {
            "fact_a": "Third Fact A",
            "fact_b": "Second Fact B",
            "fact_c": "First Fact C",
        },
    }

    accumulator.add(chunk_1)
    accumulator.add(chunk_2)
    accumulator.add(chunk_0)

    result = accumulator.get_final_result()
    facts = result["extracted_facts"]

    assert facts["fact_a"] == "First Fact A"
    assert facts["fact_b"] == "First Fact B"
    assert facts["fact_c"] == "First Fact C"


def test_chunk_accumulator_reducer_xai_extensions() -> None:
    """Verify nested dynamic XAI extensions are successfully merged with collision handling."""
    accumulator = ChunkAccumulator()

    chunk_0: dict[str, Any] = {
        "chunk_index": 0,
        "matrix_toulmin": {
            "falsification": "The model is unstable.",
            "citations": ["doc1"],
            "confidence": 0.85,
            "flagged": True,
        },
    }
    chunk_1: dict[str, Any] = {
        "chunk_index": 1,
        "matrix_toulmin": {
            "falsification": "And lacks rigorous data.",
            "citations": ["doc2"],
            "confidence": 0.70,
            "flagged": False,
        },
    }

    accumulator.add(chunk_0)
    accumulator.add(chunk_1)

    result = accumulator.get_final_result()
    toulmin = result["matrix_toulmin"]

    # String should concatenate
    assert toulmin["falsification"] == "The model is unstable. And lacks rigorous data."
    # List should extend
    assert toulmin["citations"] == ["doc1", "doc2"]
    # Float/Int should keep minimum (0.70 < 0.85)
    assert toulmin["confidence"] == 0.70
    # Boolean should OR (True or False = True)
    assert toulmin["flagged"] is True


def test_chunk_accumulator_reducer_fail_fast_on_incompatible() -> None:
    """Verify that type collisions in dynamic XAI extensions trigger strict fail-fast."""
    accumulator = ChunkAccumulator()

    chunk_0: dict[str, Any] = {"matrix_test": {"key": "string value"}}
    chunk_1: dict[str, Any] = {"matrix_test": {"key": 123}}  # Type collision

    accumulator.add(chunk_0)
    accumulator.add(chunk_1)

    with pytest.raises(AppException) as excinfo:
        accumulator.reduce()

    assert excinfo.value.status_code == 500
    assert "Strict Fail-Fast: Unresolvable key collision" in excinfo.value.message


def test_chunk_accumulator_reducer_schema_validation() -> None:
    """Verify that the accumulator rejects chunks failing schema validation."""
    accumulator = ChunkAccumulator(response_model=MockResponseSchema)

    # Extra field in chunk
    invalid_chunk = {
        "chunk_index": 0,
        "mechanical_trace": "Trace",
        "extra_field_not_allowed": "should fail",
    }

    with pytest.raises(AppException) as excinfo:
        accumulator.add(invalid_chunk)

    assert excinfo.value.status_code == 500
    assert "Strict Fail-Fast: Chunk validation failed" in excinfo.value.message


def test_chunk_accumulator_reducer_evaluations_and_reasoning_trace() -> None:
    """Verify that evaluations list is accumulated and reasoning_trace is concatenated during reduction."""
    accumulator = ChunkAccumulator()

    chunk_0: dict[str, Any] = {
        "chunk_index": 0,
        "reasoning_trace": "First reason.",
        "evaluations": [
            {
                "atom_id": "atom_1",
                "exact_quote": "Quote 1",
                "contextual_override": False,
                "status": "PASS",
                "semantic_reasoning": "Reason 1",
            }
        ],
    }
    chunk_1: dict[str, Any] = {
        "chunk_index": 1,
        "reasoning_trace": "Second reason.",
        "evaluations": [
            {
                "atom_id": "atom_2",
                "exact_quote": "Quote 2",
                "contextual_override": True,
                "status": "DLQ",
                "semantic_reasoning": "Reason 2",
            }
        ],
    }

    accumulator.add(chunk_0)
    accumulator.add(chunk_1)

    result = accumulator.get_final_result()

    # The evaluations should be accumulated
    assert "evaluations" in result
    assert len(result["evaluations"]) == 2
    assert result["evaluations"][0]["atom_id"] == "atom_1"
    assert result["evaluations"][1]["atom_id"] == "atom_2"

    # The reasoning_trace should be concatenated
    assert "reasoning_trace" in result
    assert result["reasoning_trace"] == "First reason.\n\n[Chunk]: Second reason."
