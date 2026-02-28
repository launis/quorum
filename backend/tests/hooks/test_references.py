from unittest.mock import MagicMock, patch

import pytest

from backend.exceptions import AppException
from backend.hooks.references import generate_bibliography_hook
from backend.models.domain import BibliographyItem, BibliographyResult
from backend.models.state import WorkflowState


@pytest.mark.asyncio
async def test_generate_bibliography_hook_success():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {
        "history_text": "According to Smith (2020), AI is great.",
    }
    # Mock KB
    state.context_variables["knowledge_base"] = {
        "references": [{"id": "smith2020", "title": "AI is Great", "year": 2020, "authors": ["Smith"]}],
        "concepts": {},
    }

    # Mock ReferenceManager inside the hook
    with patch("backend.hooks.references.ReferenceManager") as MockRM:
        instance = MockRM.return_value
        # mocking advanced_scan to return a map
        # ReferenceManager.advanced_scan returns a CitationReport object, but the hook expects
        # it to have a relevance_map attribute.
        mock_report = MagicMock()
        mock_report.relevance_map = {"Smith (2020) 'AI is Great'": ["Direct citation found."]}
        instance.advanced_scan.return_value = mock_report

        new_state = await generate_bibliography_hook(state)

        result = new_state.context_variables.get("bibliography_result")
        assert isinstance(result, BibliographyResult)
        assert len(result.references) == 1
        item = result.references[0]
        assert isinstance(item, BibliographyItem)
        # ID is hash-based in hook now
        assert item.title == "Smith (2020) 'AI is Great'"
        assert item.snippet == "Direct citation found."


@pytest.mark.asyncio
async def test_generate_bibliography_hook_empty_text():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {"history_text": ""}

    new_state = await generate_bibliography_hook(state)
    # Should skip efficiently
    assert not new_state.context_variables.get("bibliography_result")


@pytest.mark.asyncio
async def test_generate_bibliography_hook_fail_fast_on_error():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {"history_text": "Some text"}
    # Missing KB -> Should Fail Fast
    with pytest.raises(AppException) as exc:
        await generate_bibliography_hook(state)

    assert "SERVICE_DEPENDENCY_MISSING" in str(exc.value.details)



