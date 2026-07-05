from pydantic import ValidationError
import pytest
from backend_v2.models.dtos.lightweight_matrix import LightweightExtractionAtom
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote

def test_lightweight_extraction_atom_accepts_chat_log_source_id():
    """Test that a LightweightExtractionAtom accepts 'chat_log' as a source_id."""
    
    # This should work but currently fails because AliasEngine.ALIAS_REGEX_PATTERN requires \d+$
    try:
        atom = LightweightExtractionAtom.model_validate({
            "atom_id": "atom_1",
            "used_source_aliases": ["chat_log"],
            "extracted_facts": {},
            "exact_quotes": [
                {"text": "Some quote", "source_id": "chat_log"}
            ],
            "status": "PASS",
            "confidence": 0.9
        }, context={"alias_map": {}, "allowed_dynamic_keys": ["chat_log"]})
        assert atom.exact_quotes[0].source_id == "chat_log"
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly: {e}")
