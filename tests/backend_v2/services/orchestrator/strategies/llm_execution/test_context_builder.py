import pytest
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder

def test_project_compressed_strips_original_text_and_raw_content():
    """Test that _project_compressed recursively removes original_text and raw_content."""
    payload = {
        "id": "123",
        "original_text": "This is a massive string",
        "raw_content": "This is another massive string",
        "shuffled_atoms": ["atom1"],
        "nested": {
            "keep": "this",
            "original_text": "remove this too",
            "raw_content": "and this",
            "source_quote": "KEEP THIS"
        },
        "list_data": [
            {
                "original_text": "delete me",
                "raw_content": "delete me too",
                "value": "keep"
            }
        ]
    }
    
    result = ContextBuilder._project_compressed(payload)
    
    assert "original_text" not in result
    assert "raw_content" not in result
    assert "shuffled_atoms" not in result
    
    assert "original_text" not in result["nested"]
    assert "raw_content" not in result["nested"]
    assert result["nested"]["keep"] == "this"
    assert result["nested"]["source_quote"] == "KEEP THIS"
    
    assert "original_text" not in result["list_data"][0]
    assert "raw_content" not in result["list_data"][0]
    assert result["list_data"][0]["value"] == "keep"
