from collections.abc import Awaitable
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.input_processing import process_inputs
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, QuestionAnswerPair
from backend_v2.models.execution_core import ExecutionMetadata


class MockRepository:
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

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return {}


def test_guided_reflection_dto_valid_dict() -> None:
    """Test that a valid flat dictionary is correctly mapped to the strict schema."""
    raw_data = {
        "pairs": [
            {"question": "What is the primary challenge?", "answer": "Scaling the database."},
            {"question": "How are we solving it?", "answer": "Sharding."},
        ],
        "metadata": {"session_id": "xyz-123"},
    }

    dto = GuidedReflectionInputDTO.model_validate(raw_data)

    assert len(dto.pairs) == 2
    assert dto.pairs[0].question == "What is the primary challenge?"
    assert dto.pairs[0].answer == "Scaling the database."
    assert dto.pairs[1].question == "How are we solving it?"
    assert dto.pairs[1].answer == "Sharding."

    # Metadata should capture non-Q/A keys
    assert "session_id" in dto.metadata
    assert dto.metadata["session_id"] == "xyz-123"


def test_guided_reflection_dto_invalid_empty() -> None:
    """Test that an empty dictionary or dict without Q/A pairs raises ValidationError."""
    raw_data = {"random_key": "some_value"}

    with pytest.raises(ValidationError) as exc:
        GuidedReflectionInputDTO.model_validate(raw_data)

    assert "field required" in str(exc.value).lower()


def test_guided_reflection_dto_to_markdown() -> None:
    """Test the deterministic Markdown serialization of the DTO."""
    dto = GuidedReflectionInputDTO(
        pairs=[
            QuestionAnswerPair(question="Q1", answer="A1"),
            QuestionAnswerPair(question="Q2", answer="A2"),
        ],
        metadata={"user_id": "usr_99"},
    )
    md = dto.to_markdown(title="Test Questionnaire")

    assert '<questionnaire title="Test Questionnaire">' in md
    assert "<user_id>usr_99</user_id>" in md
    assert "<question>Q1</question>" in md
    assert "<answer>A1</answer>" in md
    assert "<question>Q2</question>" in md
    assert "<answer>A2</answer>" in md


@pytest.mark.asyncio
async def test_process_inputs_valid_questionnaire(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the input hook correctly validates and parses a questionnaire dictionary."""
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
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    # Mock storage to avoid writing actual files during tests
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

    # Ensure English-Only Mandate is NOT injected via naked string concatenation
    # (PromptCompiler will handle it structurally via <ai_context_mandate>)
    questionnaire_text = processed["QUESTIONNAIRE"]
    assert "--- AI INSTRUCTION FOR THIS SOURCE (QUESTIONNAIRE) ---" not in questionnaire_text
    assert "Analyze this form." not in questionnaire_text
    assert '<questionnaire title="My Form">' in questionnaire_text
    assert "<question>How are you?</question>" in questionnaire_text
    assert "<answer>I am fine.</answer>" in questionnaire_text

    doc_text = processed["DOCUMENT_TEXT"]
    assert "--- AI INSTRUCTION FOR THIS SOURCE (DOCUMENT_TEXT) ---" not in doc_text
    assert "Analyze this text." not in doc_text
    assert "Plain text input." in doc_text


@pytest.mark.asyncio
async def test_process_inputs_invalid_questionnaire(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the input hook correctly raises Fail-Fast validation error on bad dictionary."""
    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_123",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"QUESTIONNAIRE": {"not_a_questionnaire": "This should fail because no Q/A pairs exist."}}
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
    )

    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], process_inputs(state, deps))

    assert exc.value.status_code == 400
    assert "Invalid questionnaire format for 'QUESTIONNAIRE'" in exc.value.message


@pytest.mark.asyncio
async def test_process_inputs_with_spacy_and_presidio(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that SpaCy smoothing and Presidio masking are invoked via background threads when enabled."""

    class FeatureFlagMockRepository:
        async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
            return {
                "id": "wor_1234567890abcdef12",
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "slug": "test-wf-features",
                "name": {"translations": {"en": "WF", "fi": "WF"}},
                "description": {"translations": {"en": "Desc", "fi": "Desc"}},
                "status": "draft",
                "version": 1,
                "default_profile_id": "prof_123",
                "enable_semantic_smoothing": True,
                "enable_eager_anonymization": True,
                "expected_inputs": [
                    {
                        "input_key": "DOCUMENT_TEXT",
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
        workflow_id="wf_features",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"DOCUMENT_TEXT": "Raw <br> text with PII like Matti Meikäläinen."}),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi"}),
    )

    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, FeatureFlagMockRepository()),
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

    # Mock asyncio.to_thread
    async def mock_to_thread(func: Any, *args: Any, **kwargs: Any) -> Any:
        if func.__name__ == "smooth_text":
            return "Smoothed text."
        if func.__name__ == "mask_pii":
            return "Masked text."
        return func(*args, **kwargs)

    import asyncio

    monkeypatch.setattr(asyncio, "to_thread", mock_to_thread)

    result = await cast(Awaitable[HookResult], process_inputs(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    processed = result.state_delta.delta["inputs"]
    assert "DOCUMENT_TEXT" in processed
    # Due to ordering in the hook, Presidio masks the output of SpaCy.
    assert "Masked text." in processed["DOCUMENT_TEXT"]
    assert "Analyze this text." not in processed["DOCUMENT_TEXT"]
