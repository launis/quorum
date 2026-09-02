from collections.abc import Awaitable
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.input_processing import _process_chat_history, process_inputs
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO


@pytest.mark.asyncio
@patch("backend_v2.hooks.input_processing.ChatParserService.parse_pasted_chat")
async def test_process_chat_history_separates_speakers(mock_parse: Any) -> None:
    mock_parse.return_value = ChatHistoryDTO(
        conversation=[
            ChatMessageDTO(role="user", content="Hello AI!"),
            ChatMessageDTO(role="ai", content="Hello User!"),
            ChatMessageDTO(role="user", content="What is 2+2?"),
        ]
    )

    with patch("backend_v2.hooks.input_processing.get_pii_service"):
        result = await _process_chat_history(
            resolved_text="some text",
            key="chat_log",
            system_repo=None,
            enable_semantic_smoothing=False,
            enable_eager_anonymization=False,
            language="en",
        )

    expected_combined = (
        "<user_payload>\nHello AI!\n</user_payload>\n\n"
        "<ai_draft_context>\nHello User!\n</ai_draft_context>\n\n"
        "<user_payload>\nWhat is 2+2?\n</user_payload>"
    )
    assert result["combined"] == expected_combined
    assert result["user_only"] == "Hello AI!\n\nWhat is 2+2?"
    assert result["ai_only"] == "Hello User!"


@pytest.mark.asyncio
async def test_process_chat_history_bypasses_nlp_for_json() -> None:
    json_input = """
    {
        "conversation": [
            {"role": "user", "content": "Hello"}
        ]
    }
    """
    with patch("backend_v2.hooks.input_processing.ChatParserService.parse_pasted_chat") as mock_parse:
        with patch("backend_v2.hooks.input_processing.get_pii_service") as mock_get_pii:
            result = await _process_chat_history(
                resolved_text=json_input,
                key="chat_log",
                system_repo=None,
                enable_semantic_smoothing=True,
                enable_eager_anonymization=True,
                language="en",
            )

            mock_get_pii.assert_not_called()
            mock_parse.assert_not_called()

            assert result["combined"] == "<user_payload>\nHello\n</user_payload>"
            assert result["user_only"] == "Hello"


@pytest.mark.asyncio
async def test_process_inputs_missing_context() -> None:
    state = HookState(
        workflow_id="",
        execution_id="",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock()

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)

    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_process_inputs_missing_language() -> None:
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(vars={"language": ""}),
        metadata=ExecutionMetadata(),
    )

    mock_workflow_repo = MagicMock()
    mock_workflow_repo.get_workflow_by_id = AsyncMock(
        return_value={
            "id": "wor_1234567890123456",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "slug": "test_workflow",
            "name": "Test Workflow",
            "description": "desc",
            "status": "draft",
            "version": 1,
            "default_profile_id": "out_1234567890123456",
            "expected_inputs": [],
        }
    )

    deps = MagicMock()
    deps.workflow_repo = mock_workflow_repo

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)

    assert exc.value.details["error_code"] == "CONFIGURATION_ERROR"


class MockInputProcessingRepo:
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        if workflow_id == "not_found":
            return None
        return {
            "id": "wor_1234567890abcdef12",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "slug": "test-wf",
            "name": {"translations": {"en": "Test WF", "fi": "Test WF"}},
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof_123",
            "expected_inputs": [
                {
                    "input_key": "QUESTIONNAIRE",
                    "label": {"translations": {"en": "My Form", "fi": "Lomake"}},
                    "description": {"translations": {"en": "Form input", "fi": "Form input"}},
                    "input_modes": ["text"],
                    "required": True,
                    "is_chat_history": False,
                    "ai_description": "Analyze this form.",
                },
                {
                    "input_key": "DOCUMENT_TEXT",
                    "label": {"translations": {"en": "Doc", "fi": "Dokkari"}},
                    "description": {"translations": {"en": "Doc input", "fi": "Doc input"}},
                    "input_modes": ["text"],
                    "required": False,
                    "is_chat_history": False,
                    "ai_description": "Analyze this text.",
                },
            ],
        }


@pytest.mark.asyncio
async def test_process_inputs_valid_questionnaire(monkeypatch: pytest.MonkeyPatch) -> None:

    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_123",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "QUESTIONNAIRE": {
                    "pairs": [
                        {"question": "How are you?", "answer": "I am fine."},
                        {"question": "Why?", "answer": "Just because."},
                    ],
                    "metadata": {},
                },
                "DOCUMENT_TEXT": "Plain text input.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
    )

    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockInputProcessingRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await cast(Awaitable[HookResult], process_inputs(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "inputs" in result.state_delta.delta

    processed = result.state_delta.delta["inputs"]
    assert "QUESTIONNAIRE" in processed
    assert "DOCUMENT_TEXT" in processed
    assert '<questionnaire title="My Form">' in processed["QUESTIONNAIRE"]


@pytest.mark.asyncio
async def test_process_inputs_workflow_not_found() -> None:

    state = HookState(
        execution_id="test_exec",
        workflow_id="not_found",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockInputProcessingRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], process_inputs(state, deps))
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_process_inputs_missing_required_input(monkeypatch: pytest.MonkeyPatch) -> None:

    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_123",
        inputs=ExecutionInputsDTO(raw_inputs={"QUESTIONNAIRE": ""}),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockInputProcessingRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], process_inputs(state, deps))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_process_inputs_with_chat_history_step(monkeypatch: pytest.MonkeyPatch) -> None:

    class ChatWFRepo:
        async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
            return {
                "id": "wor_1234567890abcdef12",
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "slug": "chat-wf",
                "name": {"translations": {"en": "Chat WF", "fi": "Chat WF"}},
                "description": {"translations": {"en": "Desc", "fi": "Desc"}},
                "status": "draft",
                "version": 1,
                "default_profile_id": "prof_123",
                "expected_inputs": [
                    {
                        "input_key": "CHAT_LOG",
                        "label": {"translations": {"en": "Chat", "fi": "Chat"}},
                        "description": {"translations": {"en": "Chat", "fi": "Chat"}},
                        "input_modes": ["text"],
                        "required": True,
                        "is_chat_history": True,
                        "ai_description": "Analyze this chat.",
                    }
                ],
            }

    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_chat",
        inputs=ExecutionInputsDTO(raw_inputs={"CHAT_LOG": '{"conversation": [{"role": "user", "content": "Hello"}]}'}),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, ChatWFRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await cast(Awaitable[HookResult], process_inputs(state, deps))
    assert result.success is True
    assert "CHAT_LOG" in result.state_delta.delta["inputs"]
    assert "CHAT_LOG_user_only" in result.state_delta.delta["inputs"]


@pytest.mark.asyncio
async def test_process_inputs_with_smoothing_and_anonymization(monkeypatch: pytest.MonkeyPatch) -> None:

    class SmoothWFRepo:
        async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
            return {
                "id": "wor_1234567890abcdef12",
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "slug": "smooth-wf",
                "name": {"translations": {"en": "Smooth WF", "fi": "Smooth WF"}},
                "description": {"translations": {"en": "Desc", "fi": "Desc"}},
                "status": "draft",
                "version": 1,
                "default_profile_id": "prof_123",
                "enable_semantic_smoothing": True,
                "enable_eager_anonymization": True,
                "expected_inputs": [
                    {
                        "input_key": "DOC",
                        "label": {"translations": {"en": "Doc", "fi": "Doc"}},
                        "description": {"translations": {"en": "Doc", "fi": "Doc"}},
                        "input_modes": ["text"],
                        "required": True,
                        "is_chat_history": False,
                        "ai_description": "Analyze this text.",
                    }
                ],
            }

    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_smooth",
        inputs=ExecutionInputsDTO(raw_inputs={"DOC": "Matti Meikäläinen at test"}),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi"}),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, SmoothWFRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    mock_pii = MagicMock()
    mock_pii.smooth_text.return_value = "Smoothed text"
    mock_pii.mask_pii.return_value = "Masked text"
    monkeypatch.setattr("backend_v2.hooks.input_processing.get_pii_service", lambda: mock_pii)

    result = await cast(Awaitable[HookResult], process_inputs(state, deps))
    assert result.success is True
    assert result.state_delta.delta["inputs"]["DOC"] == "Masked text"


@pytest.mark.asyncio
async def test_process_inputs_dynamic_inputs_resolution(monkeypatch: pytest.MonkeyPatch) -> None:

    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_dyn",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "QUESTIONNAIRE": {
                    "pairs": [{"question": "Q", "answer": "A"}],
                    "metadata": {},
                }
            },
            dynamic_inputs={"document_text": "Dynamic input document text"},
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockInputProcessingRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await cast(Awaitable[HookResult], process_inputs(state, deps))
    assert result.success is True
    assert result.state_delta.delta["inputs"]["DOCUMENT_TEXT"] == "Dynamic input document text"


@pytest.mark.asyncio
async def test_process_inputs_missing_english_ai_description(monkeypatch: pytest.MonkeyPatch) -> None:

    class EmptyDescWFRepo:
        async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
            return {
                "id": "wor_1234567890abcdef12",
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "slug": "desc-wf",
                "name": {"translations": {"en": "WF", "fi": "WF"}},
                "description": {"translations": {"en": "Desc", "fi": "Desc"}},
                "status": "draft",
                "version": 1,
                "default_profile_id": "prof_123",
                "expected_inputs": [
                    {
                        "input_key": "DOC",
                        "label": {"translations": {"en": "Doc", "fi": "Doc"}},
                        "description": {"translations": {"en": "Doc", "fi": "Doc"}},
                        "input_modes": ["text"],
                        "required": True,
                        "is_chat_history": False,
                        "ai_description": "   ",
                    }
                ],
            }

    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_nodesc",
        inputs=ExecutionInputsDTO(raw_inputs={"DOC": "Some text"}),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, EmptyDescWFRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], process_inputs(state, deps))
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_process_inputs_with_gvars_resolution(monkeypatch: pytest.MonkeyPatch) -> None:

    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_gvars",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "QUESTIONNAIRE": {
                    "pairs": [{"question": "Q", "answer": "A"}],
                    "metadata": {},
                }
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en", "document_text": "Gvars doc text"}),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockInputProcessingRepo()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await cast(Awaitable[HookResult], process_inputs(state, deps))
    assert result.success is True
    assert result.state_delta.delta["inputs"]["DOCUMENT_TEXT"] == "Gvars doc text"


@pytest.mark.asyncio
async def test_process_chat_history_unstructured_parser_failure() -> None:
    with patch(
        "backend_v2.hooks.input_processing.ChatParserService.parse_pasted_chat",
        side_effect=RuntimeError("Parsing error"),
    ):
        with pytest.raises(AppException) as exc:
            await _process_chat_history(
                resolved_text="unstructured text",
                key="chat_key",
                system_repo=None,
                enable_semantic_smoothing=False,
                enable_eager_anonymization=False,
                language="en",
            )
        assert exc.value.status_code == 400


def test_process_questionnaire_invalid_dict() -> None:
    from backend_v2.hooks.input_processing import _process_questionnaire
    from backend_v2.models.v2_core import ExpectedInput

    expected_input = ExpectedInput(
        input_key="Q",
        label={"translations": {"en": "Label"}},
        description={"translations": {"en": "Desc"}},
        input_modes=["text"],
        required=True,
    )
    with pytest.raises(AppException) as exc:
        _process_questionnaire({"invalid": "data"}, "Q", expected_input)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_save_forensic_input_storage_error() -> None:
    from backend_v2.hooks.input_processing import _save_forensic_input

    with patch(
        "backend_v2.hooks.input_processing.get_storage_driver", side_effect=RuntimeError("Storage driver offline")
    ):
        with pytest.raises(AppException) as exc:
            await _save_forensic_input("exec_1", "key_1", "content")
        assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_process_chat_history_malformed_json_fallback_with_nlp(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_pii = MagicMock()
    mock_pii.smooth_text.return_value = "Smoothed chat text"
    mock_pii.mask_pii.return_value = "Masked chat text"
    monkeypatch.setattr("backend_v2.hooks.input_processing.get_pii_service", lambda: mock_pii)

    with patch("backend_v2.hooks.input_processing.ChatParserService.parse_pasted_chat") as mock_parse:
        mock_parse.return_value = ChatHistoryDTO(conversation=[ChatMessageDTO(role="user", content="Parsed message")])
        result = await _process_chat_history(
            resolved_text="{invalid json: true}",
            key="chat_key",
            system_repo=None,
            enable_semantic_smoothing=True,
            enable_eager_anonymization=True,
            language="en",
        )
        assert result["user_only"] == "Parsed message"


def test_process_questionnaire_missing_english_label() -> None:
    from backend_v2.hooks.input_processing import _process_questionnaire

    mock_input = MagicMock()
    mock_input.label.resolve.return_value = ""
    with pytest.raises(AppException) as exc:
        _process_questionnaire({"pairs": [{"question": "Q", "answer": "A"}]}, "Q", mock_input)
    assert exc.value.status_code == 500
