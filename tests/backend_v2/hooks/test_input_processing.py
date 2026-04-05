import base64
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.input_processing import process_inputs


class MockStorage:
    async def save(self, path: str, content: str) -> None:
        pass


class MockRepository:
    async def get_workflow_by_id(self, wf_id: str) -> dict[str, Any] | None:
        if wf_id == "wf_missing":
            return None
        return {
            "id": "wf_1234567890abcdef",
            "slug": "test_flow",
            "name": "Test",
            "description": "Test",
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof_1",
            "expected_inputs": [
                {
                    "input_key": "my_pdf",
                    "label": {"translations": {"en": "My PDF"}, "default_locale": "en"},
                    "required": True,
                    "is_chat_history": False,
                    "input_modes": ["file"],
                    "description": {"translations": {"en": "Upload PDF"}, "default_locale": "en"},
                    "ai_description": "Analyze this document.",
                },
                {
                    "input_key": "my_questionnaire",
                    "label": {"translations": {"en": "Q Auth"}, "default_locale": "en"},
                    "required": False,
                    "is_chat_history": False,
                    "input_modes": ["questionnaire"],
                    "description": {"translations": {"en": "Fill it"}, "default_locale": "en"},
                    "ai_description": "Rules for form.",
                    "questionnaire_definition": [
                        {
                            "question_id": "q1",
                            "question": {"translations": {"en": "How?"}, "default_locale": "en"},
                            "type": "text",
                        }
                    ],
                },
                {
                    "input_key": "my_chat",
                    "label": {"translations": {"en": "Chat"}, "default_locale": "en"},
                    "required": False,
                    "is_chat_history": True,
                    "input_modes": ["paste"],
                    "description": {"translations": {"en": "Paste chat"}, "default_locale": "en"},
                    "ai_description": "Analyze chat.",
                },
            ],
            "steps": [],
        }


@pytest.mark.asyncio
async def test_fail_fast_missing_input() -> None:
    """Fail-Fast: If required input is missing, throw Validation Error."""
    state = HookState(
        execution_id="exe_1",
        workflow_id="wf_1234567890abcdef",
        step_id="step_1",
        inputs={},  # Empty inputs
    )
    deps = HookDependencies(repository=cast(Any, MockRepository()))

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)  # type: ignore

    assert exc.value.status_code == 400
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


@pytest.mark.asyncio
@patch("backend_v2.services.storage.get_storage_driver")
@patch("backend_v2.hooks.input_processing._extract_pdf")
async def test_pdf_extraction_and_questionnaire_blockquote(
    mock_extract_pdf: AsyncMock, mock_get_storage: AsyncMock
) -> None:
    """Test PDF is passed to extraction and Questionnaire creates blockquotes (> **A:**)."""
    mock_extract_pdf.return_value = "# Extracted PDF Markdown\n\nData."
    mock_get_storage.return_value = MockStorage()

    fake_pdf_b64 = base64.b64encode(b"fake_pdf_bytes").decode("utf-8")

    state = HookState(
        execution_id="exe_1",
        workflow_id="wf_1234567890abcdef",
        step_id="step_1",
        inputs={
            "my_pdf": {"filename": "test.pdf", "content_base64": fake_pdf_b64},
            "my_questionnaire": {"q1": "Miten menee?", "a1": "Koneellisesti"},
        },
    )
    deps = HookDependencies(repository=cast(Any, MockRepository()))

    result = await process_inputs(state, deps)  # type: ignore
    assert result.success is True

    # Check PDF resolution and AI Instruction injection
    res_inputs = result.state_delta.get("inputs", {})
    pdf_res = res_inputs.get("my_pdf", "")
    assert "--- AI INSTRUCTION FOR THIS SOURCE (my_pdf) ---" in pdf_res
    assert "Analyze this document." in pdf_res
    assert "# Extracted PDF Markdown" in pdf_res

    # V2 AMNESIA VERIFICATION: Ensure the massive payload was destroyed in memory
    assert "content_base64" not in state.inputs["my_pdf"], "Base64 payload must be destroyed to prevent Token Explosions"

    # Check Questionnaire Blockquote isolation (Epic 12 requirement)
    q_res = res_inputs.get("my_questionnaire", "")
    assert "### Q: Miten menee?" in q_res
    assert "> **A:** Koneellisesti" in q_res


class DummyChatTurn:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class DummyChatDTO:
    def __init__(self) -> None:
        self.conversation = [
            DummyChatTurn(role="User", content="Hello AI"),
            DummyChatTurn(role="Agent", content="Greetings!"),
        ]


@pytest.mark.asyncio
@patch("backend_v2.services.storage.get_storage_driver")
@patch("backend_v2.services.chat_parser.ChatParserService.parse_pasted_chat", new_callable=AsyncMock)
@patch("backend_v2.hooks.input_processing._extract_pdf")
async def test_chat_parser_structuring(
    mock_extract_pdf: AsyncMock, mock_parse_chat: AsyncMock, mock_get_storage: AsyncMock
) -> None:
    """Test Chat History is routed to ChatParserService and converts to pure Markdown."""
    mock_extract_pdf.return_value = "A PDF with chat in it"
    mock_parse_chat.return_value = DummyChatDTO()
    mock_get_storage.return_value = MockStorage()

    state = HookState(
        execution_id="exe_1",
        workflow_id="wf_1234567890abcdef",
        step_id="step_1",
        inputs={
            "my_pdf": "Valid String to pass required check",
            "my_chat": "I pasted some raw chat history here.",
        },
    )
    deps = HookDependencies(repository=cast(Any, MockRepository()))

    result = await process_inputs(state, deps)  # type: ignore
    assert result.success is True

    res_inputs = result.state_delta.get("inputs", {})
    chat_res = res_inputs.get("my_chat", "")
    # Verify AI Instruction injection exists
    assert "--- AI INSTRUCTION FOR THIS SOURCE (my_chat) ---" in chat_res

    # Verify the DummyChatDTO was transformed into clean Markdown
    assert "**User**: Hello AI" in chat_res
    assert "**Agent**: Greetings!" in chat_res
