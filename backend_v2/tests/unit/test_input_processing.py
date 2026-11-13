"""Unit tests for GuidedReflectionInputDTO and process_inputs hook."""

from __future__ import annotations

import asyncio
import types

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

import backend_v2.services.storage
from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.input_processing import process_inputs
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, QuestionAnswerPair
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.factories.model_factories import WorkflowFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class ExpectedInputFactory(ModelFactory[ExpectedInput]):
    """Polyfactory model factory for ExpectedInput workflow input definitions."""

    __model__ = ExpectedInput
    __use_defaults__ = True


def test_guided_reflection_dto_valid_dict() -> None:
    """Test that valid JSON input is mapped to the strict GuidedReflectionInputDTO schema."""
    raw_json = (
        '{"pairs": ['
        '{"question": "What is the primary challenge?", "answer": "Scaling the database."}, '
        '{"question": "How are we solving it?", "answer": "Sharding."}'
        '], "metadata": {"session_id": "xyz-123"}}'
    )

    dto = GuidedReflectionInputDTO.model_validate_json(raw_json)

    assert len(dto.pairs) == 2
    assert dto.pairs[0].question == "What is the primary challenge?"
    assert dto.pairs[0].answer == "Scaling the database."
    assert dto.pairs[1].question == "How are we solving it?"
    assert dto.pairs[1].answer == "Sharding."

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
    """Test the input hook validates and parses a questionnaire dictionary."""
    wf_id = "wor_0195f3a00000700384567890abcdef12"
    inputs_dto = ExecutionInputsDTO.model_validate_json(
        '{"raw_inputs": {'
        '"QUESTIONNAIRE": {"pairs": ['
        '{"question": "How are you?", "answer": "I am fine."}, '
        '{"question": "Why?", "answer": "Just because."}'
        '], "metadata": {}}, '
        '"DOCUMENT_TEXT": "Plain text input."'
        '}, "dynamic_inputs": {}}'
    )
    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=inputs_dto,
        global_context_vars=GlobalContextVarsDTO(language="en"),
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        WorkflowFactory.build(
            id=wf_id,
            historical_context_mode=HistoricalContextMode.DISABLED,
            model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
            slug="test-wf",
            name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
            description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
            status="draft",
            version=1,
            default_profile_id="prf_0195f3a00000700d8ddd1111dddd1111",
            enable_semantic_smoothing=False,
            enable_eager_anonymization=False,
            expected_inputs=[
                ExpectedInputFactory.build(
                    input_key="QUESTIONNAIRE",
                    label=I18nText(translations={"en": "My Form", "fi": "Lomake"}),
                    description=I18nText(translations={"en": "Form input", "fi": "Form input"}),
                    input_modes=["text"],
                    required=True,
                    is_chat_history=False,
                    ai_description="Analyze this form.",
                ),
                ExpectedInputFactory.build(
                    input_key="DOCUMENT_TEXT",
                    label=I18nText(translations={"en": "Doc", "fi": "Dokkari"}),
                    description=I18nText(translations={"en": "Doc input", "fi": "Doc input"}),
                    input_modes=["text"],
                    required=False,
                    is_chat_history=False,
                    ai_description="Analyze this text.",
                ),
            ],
        )
    )

    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    result = await process_inputs(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ExecutionInputsDTO)

    processed = result.state_delta.delta.raw_inputs
    assert "QUESTIONNAIRE" in processed
    assert "DOCUMENT_TEXT" in processed

    questionnaire_text = processed["QUESTIONNAIRE"]
    assert isinstance(questionnaire_text, str)
    assert "--- AI INSTRUCTION FOR THIS SOURCE (QUESTIONNAIRE) ---" not in questionnaire_text
    assert "Analyze this form." not in questionnaire_text
    assert '<questionnaire title="My Form">' in questionnaire_text
    assert "<question>How are you?</question>" in questionnaire_text
    assert "<answer>I am fine.</answer>" in questionnaire_text

    doc_text = processed["DOCUMENT_TEXT"]
    assert isinstance(doc_text, str)
    assert "--- AI INSTRUCTION FOR THIS SOURCE (DOCUMENT_TEXT) ---" not in doc_text
    assert "Analyze this text." not in doc_text
    assert "Plain text input." in doc_text


@pytest.mark.asyncio
async def test_process_inputs_invalid_questionnaire(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the input hook raises Fail-Fast validation error on malformed questionnaire payload."""
    wf_id = "wor_0195f3a00000700384567890abcdef12"
    bad_inputs = ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={}).model_copy(
        update={
            "raw_inputs": {
                "QUESTIONNAIRE": {"not_a_questionnaire": "This should fail because no Q/A pairs exist."},
            }
        }
    )
    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=bad_inputs,
        global_context_vars=GlobalContextVarsDTO(language="en"),
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        WorkflowFactory.build(
            id=wf_id,
            historical_context_mode=HistoricalContextMode.DISABLED,
            model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
            slug="test-wf",
            name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
            description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
            status="draft",
            version=1,
            default_profile_id="prf_0195f3a00000700d8ddd1111dddd1111",
            expected_inputs=[
                ExpectedInputFactory.build(
                    input_key="QUESTIONNAIRE",
                    label=I18nText(translations={"en": "My Form", "fi": "Lomake"}),
                    description=I18nText(translations={"en": "Form input", "fi": "Form input"}),
                    input_modes=["text"],
                    required=True,
                    is_chat_history=False,
                    ai_description="Analyze this form.",
                ),
            ],
        )
    )

    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)

    assert exc.value.status_code == 400
    assert "Invalid questionnaire format for 'QUESTIONNAIRE'" in exc.value.message


@pytest.mark.asyncio
async def test_process_inputs_with_spacy_and_presidio(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that SpaCy smoothing and Presidio masking are invoked via background threads when enabled."""
    wf_id = "wor_0195f3a00000700c8def123456789012"
    state = HookState(
        execution_id="test_exec",
        workflow_id=wf_id,
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"DOCUMENT_TEXT": "Raw <br> text with PII like Matti Meikäläinen."},
            dynamic_inputs={},
        ),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_workflow(
        WorkflowFactory.build(
            id=wf_id,
            historical_context_mode=HistoricalContextMode.DISABLED,
            model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
            slug="test-wf-features",
            name=I18nText(translations={"en": "WF", "fi": "WF"}),
            description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
            status="draft",
            version=1,
            default_profile_id="prf_0195f3a00000700d8ddd1111dddd1111",
            enable_semantic_smoothing=True,
            enable_eager_anonymization=True,
            expected_inputs=[
                ExpectedInputFactory.build(
                    input_key="DOCUMENT_TEXT",
                    label=I18nText(translations={"en": "Doc", "fi": "Doc"}),
                    description=I18nText(translations={"en": "Doc", "fi": "Doc"}),
                    input_modes=["text"],
                    required=True,
                    is_chat_history=False,
                    ai_description="Analyze this text.",
                )
            ],
        )
    )

    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    class MockStorage:
        async def save(self, path: str, content: str) -> None:
            pass

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockStorage())

    async def mock_to_thread(func: object, *args: object, **kwargs: object) -> object:
        func_name = func.__name__ if isinstance(func, types.MethodType | types.FunctionType) else ""
        if func_name == "smooth_text":
            return "Smoothed text."
        if func_name == "mask_pii":
            return "Masked text."
        if callable(func):
            return func(*args, **kwargs)
        return None

    monkeypatch.setattr(asyncio, "to_thread", mock_to_thread)

    result = await process_inputs(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ExecutionInputsDTO)
    processed = result.state_delta.delta.raw_inputs
    assert "DOCUMENT_TEXT" in processed
    masked_doc = processed["DOCUMENT_TEXT"]
    assert isinstance(masked_doc, str)
    assert "Masked text." in masked_doc
    assert "Analyze this text." not in masked_doc
