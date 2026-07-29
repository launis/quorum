"""Unit tests for the Linguistic Directives module.

Note: The core functionality is tested extensively via `test_translation_service.py`
and `test_prompt_integration_epic90.py`. This file exists to satisfy the strict
1:1 File-to-Test matching mandate of the Universal Quality Gate (backend_audit_loop.py).
"""

from backend_v2.models.prompts.linguistic_directives import build_linguistic_context


def test_build_linguistic_context_basic_execution() -> None:
    """Ensure the function executes and returns an XML-formatted string."""
    result = build_linguistic_context(target_locale="en")
    assert "<linguistic_context>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result
