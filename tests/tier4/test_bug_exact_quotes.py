import pytest
from pydantic import ValidationError
from backend_v2.models.dtos.lightweight_matrix import LightweightExtractionAtom

def test_lightweight_extraction_atom_exact_quotes_limit():
    quotes = ["quote 1", "quote 2", "quote 3", "quote 4", "quote 5", "quote 6"]
    atom = LightweightExtractionAtom(
        atom_id="tda_123",
        extracted_facts={},
        exact_quotes=quotes,
        status="PASS",
        confidence=0.9
    )
    assert len(atom.exact_quotes) == 6
