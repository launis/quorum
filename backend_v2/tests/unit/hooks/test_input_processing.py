from typing import Any
from unittest.mock import MagicMock, patch

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
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import ChatHistoryDTO, ChatMessageDTO
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemorySystemRepository,
    InMemoryUnifiedWorkflowRepository,
)


@pytest.mark.asyncio
@patch("backend_v2.services.chat_normalizer.ChatParserService.parse_pasted_chat")
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
            system_repo=InMemorySystemRepository(),
            enable_semantic_smoothing=False,
            enable_eager_anonymization=False,
            language="en",
        )

    expected_combined = (
        "<user_payload>\n<![CDATA[Hello AI!]]>\n</user_payload>\n\n"
        "<ai_draft_context>\nHello User!\n</ai_draft_context>\n\n"
        "<user_payload>\n<![CDATA[What is 2+2?]]>\n</user_payload>"
    )
    assert result.combined == expected_combined
    assert result.user_only == "Hello AI!\n\nWhat is 2+2?"
    assert result.ai_only == "Hello User!"


@pytest.mark.asyncio
async def test_process_chat_history_scoped_nlp_on_user_turn_only() -> None:
    json_input = """
    {
        "conversation": [
            {"role": "user", "content": "Secret user data"},
            {"role": "ai", "content": "Assistant advice"}
        ]
    }
    """
    mock_pii = MagicMock()
    mock_pii.smooth_text.side_effect = lambda text, lang: f"Smoothed: {text}"
    mock_pii.mask_pii.side_effect = lambda text, lang: f"Masked: {text}"

    with patch("backend_v2.hooks.input_processing.get_pii_service", return_value=mock_pii):
        result = await _process_chat_history(
            resolved_text=json_input,
            key="chat_log",
            system_repo=InMemorySystemRepository(),
            enable_semantic_smoothing=True,
            enable_eager_anonymization=True,
            language="en",
        )

        # NLP should process ONLY user content, never AI content
        assert mock_pii.smooth_text.call_count == 1
        assert mock_pii.mask_pii.call_count == 1
        assert "Masked: Smoothed: Secret user data" in result.user_only
        assert result.ai_only == "Assistant advice"


@pytest.mark.asyncio
async def test_process_chat_history_preserves_paragraph_breaks() -> None:
    raw_chat = (
        "User: First paragraph of user.\n\nSecond paragraph of user.\n"
        "AI: Response paragraph 1.\n\nResponse paragraph 2."
    )
    result = await _process_chat_history(
        resolved_text=raw_chat,
        key="chat_log",
        system_repo=InMemorySystemRepository(),
        enable_semantic_smoothing=False,
        enable_eager_anonymization=False,
        language="en",
    )
    assert "First paragraph of user.\n\nSecond paragraph of user." in result.user_only
    assert "Response paragraph 1.\n\nResponse paragraph 2." in result.ai_only


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
    wf_id = "wor_1234567890123456"
    state = HookState(
        workflow_id=wf_id,
        execution_id="e1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(language=""),
        metadata=ExecutionMetadata(),
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
            "historical_context_mode": "DISABLED",
            "slug": "test_workflow",
            "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"translations": {"en": "desc", "fi": "desc"}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof_123",
            "expected_inputs": [],
        })
    )

    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)

    assert exc.value.details["error_code"] == "CONFIGURATION_ERROR"


@pytest.mark.asyncio
async def test_process_inputs_valid_questionnaire(monkeypatch: pytest.MonkeyPatch) -> None:
    wf_id = "wor_1234567890abcdef12"
    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
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
        global_context_vars=GlobalContextVarsDTO(language="en"),
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
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
        })
    )

    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await process_inputs(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ExecutionInputsDTO)

    processed = result.state_delta.delta.raw_inputs
    assert "QUESTIONNAIRE" in processed
    assert "DOCUMENT_TEXT" in processed
    assert '<questionnaire title="My Form">' in processed["QUESTIONNAIRE"]


@pytest.mark.asyncio
async def test_process_inputs_workflow_not_found() -> None:
    state = HookState(
        execution_id="test_exec",
        workflow_id="not_found",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        metadata=ExecutionMetadata(),
    )
    repo = InMemoryUnifiedWorkflowRepository()
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )
    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_process_inputs_missing_required_input(monkeypatch: pytest.MonkeyPatch) -> None:
    wf_id = "wor_1234567890abcdef12"
    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        inputs=ExecutionInputsDTO(raw_inputs={"QUESTIONNAIRE": ""}),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        metadata=ExecutionMetadata(),
    )
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
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
            ],
        })
    )
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_process_inputs_with_chat_history_step(monkeypatch: pytest.MonkeyPatch) -> None:
    wf_id = "wor_1234567890abcdef12"
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
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
        })
    )

    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        inputs=ExecutionInputsDTO(raw_inputs={"CHAT_LOG": '{"conversation": [{"role": "user", "content": "Hello"}]}'}),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    saved_files: list[str] = []

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            saved_files.append(path)

    monkeypatch.setattr("backend_v2.hooks.input_processing.get_storage_driver", lambda: MockStorage())

    result = await process_inputs(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ExecutionInputsDTO)
    assert "CHAT_LOG" in result.state_delta.delta.raw_inputs
    assert "CHAT_LOG_user_only" in result.state_delta.delta.raw_inputs
    assert "CHAT_LOG_ai_only" in result.state_delta.delta.raw_inputs
    assert any("input_CHAT_LOG.md" in p for p in saved_files)
    assert any("input_CHAT_LOG_user_only.md" in p for p in saved_files)
    assert any("input_CHAT_LOG_ai_only.md" in p for p in saved_files)


@pytest.mark.asyncio
async def test_process_inputs_with_smoothing_and_anonymization(monkeypatch: pytest.MonkeyPatch) -> None:
    wf_id = "wor_1234567890abcdef12"
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
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
        })
    )

    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        inputs=ExecutionInputsDTO(raw_inputs={"DOC": "Matti Meikäläinen at test"}),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
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

    result = await process_inputs(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ExecutionInputsDTO)
    assert result.state_delta.delta.raw_inputs["DOC"] == "Masked text"


@pytest.mark.asyncio
async def test_process_inputs_dynamic_inputs_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    wf_id = "wor_1234567890abcdef12"
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
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
        })
    )

    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "QUESTIONNAIRE": {
                    "pairs": [{"question": "Q", "answer": "A"}],
                    "metadata": {},
                }
            },
            dynamic_inputs={"document_text": "Dynamic input document text"},
        ),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await process_inputs(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ExecutionInputsDTO)
    assert result.state_delta.delta.raw_inputs["DOCUMENT_TEXT"] == "Dynamic input document text"


@pytest.mark.asyncio
async def test_process_inputs_missing_english_ai_description(monkeypatch: pytest.MonkeyPatch) -> None:
    wf_id = "wor_1234567890abcdef12"
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
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
        })
    )

    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        inputs=ExecutionInputsDTO(raw_inputs={"DOC": "Some text"}),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )
    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_process_inputs_with_gvars_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    wf_id = "wor_1234567890abcdef12"
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        Workflow.model_validate({
            "id": wf_id,
            "model_registry_id": "cfg_model_registry_01",
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
        })
    )

    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "QUESTIONNAIRE": {
                    "pairs": [{"question": "Q", "answer": "A"}],
                    "metadata": {},
                }
            },
            dynamic_inputs={"document_text": "Gvars doc text"},
        ),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        metadata=ExecutionMetadata(),
    )
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await process_inputs(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ExecutionInputsDTO)
    assert result.state_delta.delta.raw_inputs["DOCUMENT_TEXT"] == "Gvars doc text"


@pytest.mark.asyncio
async def test_process_chat_history_unstructured_parser_failure() -> None:
    with patch(
        "backend_v2.services.chat_normalizer.ChatParserService.parse_pasted_chat",
        side_effect=RuntimeError("Parsing error"),
    ):
        with pytest.raises(AppException) as exc:
            await _process_chat_history(
                resolved_text="unstructured text",
                key="chat_key",
                system_repo=InMemorySystemRepository(),
                enable_semantic_smoothing=False,
                enable_eager_anonymization=False,
                language="en",
            )
        assert exc.value.status_code == 400


def test_process_questionnaire_invalid_dict() -> None:
    from backend_v2.hooks.input_processing import _process_questionnaire
    from backend_v2.models.domain.step import ExpectedInput

    expected_input = ExpectedInput(
        input_key="Q",
        label=I18nText(translations={"en": "Label"}),
        description=I18nText(translations={"en": "Desc"}),
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

    with patch("backend_v2.services.chat_normalizer.ChatParserService.parse_pasted_chat") as mock_parse:
        mock_parse.return_value = ChatHistoryDTO(conversation=[ChatMessageDTO(role="user", content="Parsed message")])
        result = await _process_chat_history(
            resolved_text="{invalid json: true}",
            key="chat_key",
            system_repo=InMemorySystemRepository(),
            enable_semantic_smoothing=True,
            enable_eager_anonymization=True,
            language="en",
        )
        assert result.user_only == "Masked chat text"


def test_process_questionnaire_localized_and_fallback_label() -> None:
    from backend_v2.hooks.input_processing import _process_questionnaire
    from backend_v2.models.domain.step import ExpectedInput

    # 1. Resolves Finnish label when target_locale is fi
    fi_input = ExpectedInput(
        input_key="kyselylomake",
        label=I18nText(translations={"en": "Self-Assessment", "fi": "Itsearviointi"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        input_modes=["text"],
        required=True,
    )
    res_fi = _process_questionnaire(
        {"pairs": [{"question": "Miten menee?", "answer": "Hyvin."}]},
        "kyselylomake",
        fi_input,
        target_locale="fi",
    )
    assert '<questionnaire title="Itsearviointi">' in res_fi

    # 2. Resolves Swedish label when target_locale is sv
    sv_input = ExpectedInput(
        input_key="enkat",
        label=I18nText(translations={"en": "Self-Assessment", "sv": "Självutvärdering"}),
        description=I18nText(translations={"en": "Description", "sv": "Beskrivning"}),
        input_modes=["text"],
        required=True,
    )
    res_sv = _process_questionnaire(
        {"pairs": [{"question": "Hur mår du?", "answer": "Bra."}]},
        "enkat",
        sv_input,
        target_locale="sv",
    )
    assert '<questionnaire title="Självutvärdering">' in res_sv

    # 3. Falls back to English label when target_locale translation is missing
    fallback_input = ExpectedInput(
        input_key="missing_loc",
        label=I18nText(translations={"en": "English Fallback"}),
        description=I18nText(translations={"en": "Description"}),
        input_modes=["text"],
        required=True,
    )
    res_en = _process_questionnaire(
        {"pairs": [{"question": "Q?", "answer": "A."}]},
        "missing_loc",
        fallback_input,
        target_locale="fi",
    )
    assert '<questionnaire title="English Fallback">' in res_en

    # 4. Falls back gracefully to key when resolve returns empty string
    mock_input = MagicMock()
    mock_input.label.resolve.return_value = ""
    res_key = _process_questionnaire(
        {"pairs": [{"question": "Q?", "answer": "A."}]},
        "fallback_key",
        mock_input,
        target_locale="fi",
    )
    assert '<questionnaire title="fallback_key">' in res_key
