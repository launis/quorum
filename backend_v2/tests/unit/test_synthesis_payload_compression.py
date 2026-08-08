import json
from backend_v2.services.orchestrator.synthesis_distiller import _compress_synthesis_payload

def test_compress_synthesis_payload_leaks_atom_quotes() -> None:
    """PROMISE: Prove that _compress_synthesis_payload strips evaluations but leaks massive atom_quotes."""
    
    # Arrange: Create a payload with both evaluations and atom_quotes
    massive_string = "A" * 1000000  # 1 million chars
    
    payload = {
        "evaluations": [
            {
                "atom_id": "a0",
                "exact_quotes": [{"quote": massive_string}],
                "semantic_reasoning": massive_string
            }
        ],
        "atom_quotes": {
            "blk_123": [
                {"level": 5, "level_name": "High", "quote": massive_string}
            ]
        }
    }
    
    # Act: Compress the payload
    compressed_str = _compress_synthesis_payload(payload)
    compressed_dict = json.loads(compressed_str)
    
    # Assert: Evaluations should be aggressively pruned (capped to 300 chars)
    pruned_evals = compressed_dict.get("evaluations", [])
    assert len(pruned_evals) == 1
    assert len(pruned_evals[0]["exact_quotes"][0]) <= 300
    assert len(pruned_evals[0]["semantic_reasoning"]) <= 300
    
    # Assert EXPECTED architecture behavior: the overall payload should be strictly bounded to prevent context window explosion.
    # It should strip atom_quotes or prune it heavily, so the string should be small.
    assert len(compressed_str) < 5000, f"ContextWindowExceededError Risk: Compressed payload is too large ({len(compressed_str)} characters) due to unpruned atom_quotes."
