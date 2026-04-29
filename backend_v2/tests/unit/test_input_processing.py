from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.input_processing import process_inputs
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, QuestionAnswerPair


class MockRepository:
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        if workflow_id == "not_found":
            return None
        return {
            "id": "wor_1234567890abcdef12",
            "slug": "test-wf",
            "name": {"translations": {"en": "Test WF"}, "default_locale": "en"},
            "description": {"translations": {"en": "Desc"}, "default_locale": "en"},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof_123",
            "expected_inputs": [
                {
                    "input_key": "QUESTIONNAIRE",
                    "label": {"translations": {"en": "My Form", "fi": "Lomake"}, "default_locale": "en"},
                    "description": {"translations": {"en": "Form input"}, "default_locale": "en"},
                    "input_modes": ["text"],
                    "required": True,
                    "is_chat_history": False,
                    "ai_description": "Analyze this form.",
                },
                {
                    "input_key": "DOCUMENT_TEXT",
                    "label": {"translations": {"en": "Doc", "fi": "Dokkari"}, "default_locale": "en"},
                    "description": {"translations": {"en": "Doc input"}, "default_locale": "en"},
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
        "q0": "What is the primary challenge?",
        "a0": "Scaling the database.",
        "q1": "How are we solving it?",
        "a1": "Sharding.",
        "session_id": "xyz-123",
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

    assert "at least one question-answer pair" in str(exc.value).lower()


def test_guided_reflection_dto_to_markdown() -> None:
    """Test the deterministic Markdown serialization of the DTO."""
    dto = GuidedReflectionInputDTO(
        pairs=[QuestionAnswerPair(question="Q1", answer="A1"), QuestionAnswerPair(question="Q2", answer="A2")],
        metadata={"user_id": "usr_99"},
    )

    md = dto.to_markdown("Test Questionnaire")

    assert "# Test Questionnaire" in md
    assert "**user_id:** usr_99" in md
    assert "### Q: Q1" in md
    assert "> **A:** A1" in md
    assert "### Q: Q2" in md
    assert "> **A:** A2" in md


@pytest.mark.asyncio
async def test_process_inputs_valid_questionnaire(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the input hook correctly validates and parses a questionnaire dictionary."""
    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_123",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={
            "QUESTIONNAIRE": {"q0": "How are you?", "a0": "I am fine.", "q1": "Why?", "a1": "Just because."},
            "DOCUMENT_TEXT": "Plain text input.",
        },
        global_context_vars={},
    )
    from typing import cast

    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=AsyncMock(),
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

    from collections.abc import Awaitable

    result = await cast(Awaitable[HookResult], process_inputs(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "inputs" in result.state_delta

    processed = result.state_delta["inputs"]
    assert "QUESTIONNAIRE" in processed
    assert "DOCUMENT_TEXT" in processed

    # Check English-Only Mandate injection and Markdown serialization
    questionnaire_text = processed["QUESTIONNAIRE"]
    assert "--- AI INSTRUCTION FOR THIS SOURCE (QUESTIONNAIRE) ---" in questionnaire_text
    assert "Analyze this form." in questionnaire_text
    assert "# My Form" in questionnaire_text
    assert "### Q: How are you?" in questionnaire_text
    assert "> **A:** I am fine." in questionnaire_text

    doc_text = processed["DOCUMENT_TEXT"]
    assert "--- AI INSTRUCTION FOR THIS SOURCE (DOCUMENT_TEXT) ---" in doc_text
    assert "Analyze this text." in doc_text
    assert "Plain text input." in doc_text


@pytest.mark.asyncio
async def test_process_inputs_invalid_questionnaire(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the input hook correctly raises Fail-Fast validation error on bad dictionary."""
    state = HookState(
        execution_id="test_exec",
        workflow_id="wf_123",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={"QUESTIONNAIRE": {"not_a_questionnaire": "This should fail because no Q/A pairs exist."}},
        global_context_vars={},
    )
    from collections.abc import Awaitable
    from typing import cast

    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], process_inputs(state, deps))

    assert exc.value.status_code == 400
    assert "Invalid questionnaire format for 'QUESTIONNAIRE'" in exc.value.message
