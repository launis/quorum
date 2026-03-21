from typing import Any
from unittest.mock import MagicMock

import pytest

from backend_v2.core.hook_registry import HookExecutionContext
from backend_v2.hooks.validation import verify_output_language


@pytest.mark.asyncio
async def test_verify_output_language_detects_english_leakage() -> None:
    # Arrange
    mock_repo = MagicMock()
    ctx = HookExecutionContext(
        repository=mock_repo,
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata={"target_locale": "fi"}
    )

    # English text with heavy stop words
    data = {"evaluation_notes": "The user was very good and the system is fine."}

    # Act
    result: dict[str, Any] = await verify_output_language(data, ctx)  # type: ignore

    # Assert
    assert "_system_warnings" in result
    assert len(result["_system_warnings"]) == 1
    assert result["_system_warnings"][0]["error_code"] == "VALIDATION_FAILED"
    assert "leaked English" in result["_system_warnings"][0]["detail"]


@pytest.mark.asyncio
async def test_verify_output_language_ignores_finnish_text() -> None:
    mock_repo = MagicMock()
    ctx = HookExecutionContext(
        repository=mock_repo,
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata={"target_locale": "fi"}
    )

    # Finnish text lacking English stop words
    data = {"evaluation_notes": "Käyttäjä vaikutti erittäin fiksulta ja ymmärsi asian täydellisesti."}

    result: dict[str, Any] = await verify_output_language(data, ctx)  # type: ignore

    # Assert no warnings injected
    assert "_system_warnings" not in result


@pytest.mark.asyncio
async def test_verify_output_language_allows_english_when_target_en() -> None:
    mock_repo = MagicMock()
    ctx = HookExecutionContext(
        repository=mock_repo,
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata={"target_locale": "en"}
    )

    # English text when English is requested
    data = {"evaluation_notes": "The user was very good and the system is fine."}

    result: dict[str, Any] = await verify_output_language(data, ctx)  # type: ignore

    # Assert
    assert "_system_warnings" not in result
