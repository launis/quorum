from backend_v2.models.dtos.lightweight_matrix import LightweightExtractionAtom
from backend_v2.models.enums import SystemConcurrency


def test_lightweight_extraction_atom_exceeds_max_quotes():
    """TDD Repro: If the LLM generates 7 quotes (exceeding the hard limit of 6 during fast dev),
    it currently crashes the entire DAG with a ValidationError.
    """
    # Generate enough quotes to exactly exceed whatever the current schema limit is
    max_limit = SystemConcurrency.SCHEMA_MAX_QUOTES.value
    quotes_list = [{"text": f"quote {i}", "source_alias": "N/A"} for i in range(max_limit + 1)]

    payload = {"atom_id": "test_atom", "exact_quotes": quotes_list, "status": "PASS", "confidence": 0.9}

    # Tier 4 TDD Repro (GREEN): The atom should now gracefully truncate the list
    # instead of crashing with a ValidationError.
    atom = LightweightExtractionAtom.model_validate(payload)

    assert len(atom.exact_quotes) == SystemConcurrency.SCHEMA_MAX_QUOTES.value
    print(f"BUG FIXED: Truncated {len(quotes_list)} quotes to {len(atom.exact_quotes)}")
