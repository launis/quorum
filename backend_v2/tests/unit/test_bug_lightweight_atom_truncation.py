from unittest.mock import AsyncMock
from backend_v2.models.dtos.lightweight_matrix import LightweightExtractionAtom
from backend_v2.settings import get_settings


def test_lightweight_extraction_atom_exceeds_max_quotes():
    """TDD Repro: If the LLM generates 7 quotes (exceeding the hard limit of 6 during fast dev),
    it currently crashes the entire DAG with a ValidationError.
    """
    settings = get_settings()
    # Generate enough quotes to exactly exceed whatever the current schema limit is
    max_limit = settings.schema_max_quotes_target + 5
    quotes_list = [{"text": f"quote {i}", "source_alias": "N/A"} for i in range(max_limit + 1)]

    payload = {"atom_id": "test_atom", "exact_quotes": quotes_list, "status": "PASS", "confidence": 0.9}

    # Tier 4 TDD Repro (GREEN): The atom should now gracefully truncate the list
    # instead of crashing with a ValidationError.
    atom = LightweightExtractionAtom.model_validate(payload)

    assert len(atom.exact_quotes) == max_limit
    print(f"BUG FIXED: Truncated {len(quotes_list)} quotes to {len(atom.exact_quotes)}")
