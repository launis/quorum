
import pytest
from unittest.mock import MagicMock, patch
from backend.hooks.references import generate_bibliography_hook, generate_bibliography
from backend.models.state import WorkflowState
from backend.models.domain import BibliographyResult, BibliographyItem
from backend.exceptions import AppException

def test_generate_bibliography_hook_success():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {
        "history_text": "According to Smith (2020), AI is great.",
    }
    # Mock KB
    state.context_variables["knowledge_base"] = {
        "references": [
            {"id": "smith2020", "title": "AI is Great", "year": 2020, "authors": ["Smith"]}
        ],
        "concepts": {}
    }
    
    # Mock ReferenceManager inside the hook to avoid complex logic deps
    # But wait, ReferenceManager is imported directly. We should mock it.
    with patch("backend.hooks.references.ReferenceManager") as MockRM:
        instance = MockRM.return_value
        # mocking advanced_scan to return a map
        instance.advanced_scan.return_value = {
            "Smith (2020) 'AI is Great'": {
                "source_id": "smith2020",
                "title": "AI is Great",
                "url": "http://example.com"
            }
        }
        
        new_state = generate_bibliography_hook(state)
        
        result = new_state.context_variables.get("bibliography_result")
        assert isinstance(result, BibliographyResult)
        assert len(result.references) == 1
        item = result.references[0]
        assert isinstance(item, BibliographyItem)
        assert item.source_id == "smith2020"
        assert item.title == "AI is Great"
        assert item.url == "http://example.com"

def test_generate_bibliography_hook_empty_text():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {"history_text": ""}
    
    new_state = generate_bibliography_hook(state)
    # Should skip efficiently
    assert not new_state.context_variables.get("bibliography_result")

def test_generate_bibliography_hook_fail_fast_on_error():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {"history_text": "Some text"}
    
    # Force error in ReferenceManager
    with patch("backend.hooks.references.ReferenceManager") as MockRM:
        MockRM.side_effect = Exception("DB Connection Failed")
        
        with pytest.raises(AppException) as exc:
            generate_bibliography_hook(state)
        
        assert "REFERENCES_GENERATION_FAILED" in str(exc.value.details)

def test_generate_bibliography_legacy_string_handling():
    # Test handling of string-only returns from RM (if that ever happens)
    # or ensure we support mismatched formats gracefully-ish (but strict on output)
    pass
