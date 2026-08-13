import json

from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor


def test_compress_synthesis_payload_strips_atom_quotes() -> None:
    """PROMISE: Prove that _compress_synthesis_payload strips evaluations and strips massive atom_quotes."""
    # Arrange: Create a payload with both evaluations and atom_quotes
    massive_string = "A" * 1000000  # 1 million chars

    payload = {
        "evaluations": [
            {"atom_id": "a0", "exact_quotes": [{"quote": massive_string}], "semantic_reasoning": massive_string}
        ],
        "atom_quotes": {"blk_123": [{"level": 5, "level_name": "High", "quote": massive_string}]},
    }

    # Act: Compress the payload
    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    compressed_dict = json.loads(compressed_str)

    # Assert: Evaluations should be aggressively pruned (capped to 300 chars)
    pruned_evals = compressed_dict.get("evaluations", [])
    assert len(pruned_evals) == 1
    assert len(pruned_evals[0]["exact_quotes"][0]) <= 300
    assert len(pruned_evals[0]["semantic_reasoning"]) <= 300

    # Assert EXPECTED architecture behavior: the overall payload should be strictly bounded to prevent context window explosion.
    # It should strip atom_quotes or prune it heavily, so the string should be small.
    assert len(compressed_str) < 5000, (
        f"ContextWindowExceededError Risk: Compressed payload is too large ({len(compressed_str)} characters) due to unpruned atom_quotes."
    )


def test_compress_synthesis_payload_negative_empty_input() -> None:
    """PROMISE: Prove that _compress_synthesis_payload handles empty/missing inputs safely."""
    # Act: Compress empty structures
    compressed_empty_dict = SynthesisPayloadCompressor.compress_synthesis_payload({})
    compressed_empty_list = SynthesisPayloadCompressor.compress_synthesis_payload([])

    # Assert: Should return safe serialized strings without crashing
    assert compressed_empty_dict == "{}"
    assert compressed_empty_list == "[]"


def test_compress_synthesis_payload_negative_invalid_types() -> None:
    """PROMISE: Prove that _compress_synthesis_payload does not crash on invalid payload structures."""
    # Arrange: Create a payload with invalid types for expected keys
    payload = {
        "evaluations": "This should be a list, not a string",
        "atom_quotes": 12345,  # This should be a dict/list, not an int
        "shuffled_atoms": {"wrong": "type"},
        "nested": {"atom_quotes": None, "evaluations": {"invalid": "dict instead of list"}},
    }

    # Act: Compress the payload
    # If the function is safely implemented, it will either pop the keys or ignore them, but will NOT crash with AttributeError or TypeError.
    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    compressed_dict = json.loads(compressed_str)

    # Assert: The payload is successfully processed and heavy keys are stripped or nullified safely
    assert compressed_dict.get("evaluations") is None
    assert "atom_quotes" not in compressed_dict
    assert "shuffled_atoms" not in compressed_dict

    nested = compressed_dict.get("nested", {})
    assert "atom_quotes" not in nested
    assert nested.get("evaluations") is None
