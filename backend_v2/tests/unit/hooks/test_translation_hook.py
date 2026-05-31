from collections.abc import Awaitable
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.hooks.translation_hook import translation_hook


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_translation_hook_skips_when_target_en(mock_repository: AsyncMock) -> None:
    """Ensure it skips translation cleanly when language is 'en'."""
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={"target_locale": "en"},
        global_context_vars={},
        inputs={"language": "en", "data": "value"},
    )
    deps = HookDependencies(
        exec_repo=mock_repository,
        workflow_repo=mock_repository,
        comp_repo=mock_repository,
        identity_repo=mock_repository,
        audit_repo=mock_repository,
        system_repo=mock_repository,
    )  # noqa: E501

    res = await cast(Awaitable[HookResult], translation_hook(state, deps))

    assert res.success is True
    assert res.state_delta == {}


@pytest.mark.asyncio
async def test_translation_hook_crashes_when_missing_language_or_locale(mock_repository: AsyncMock) -> None:  # noqa: E501
    """Ensure it drops into AppException when language or target_locale is missing."""
    # Missing target_locale
    state1 = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        metadata={},
        global_context_vars={},
        inputs={"language": "en", "data": "value"},
    )
    deps = HookDependencies(
        exec_repo=mock_repository,
        workflow_repo=mock_repository,
        comp_repo=mock_repository,
        identity_repo=mock_repository,
        audit_repo=mock_repository,
        system_repo=mock_repository,
    )  # noqa: E501

    from backend_v2.exceptions import AppException

    with pytest.raises(AppException) as exc1:
        await cast(Awaitable[HookResult], translation_hook(state1, deps))
    assert exc1.value.status_code == 400
    assert "target_locale" in exc1.value.message

    # Missing language
    state2 = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        metadata={"target_locale": "fi"},
        global_context_vars={},
        inputs={"data": "value"},
    )
    with pytest.raises(AppException) as exc2:
        await cast(Awaitable[HookResult], translation_hook(state2, deps))
    assert exc2.value.status_code == 400
    assert "language" in exc2.value.message


@pytest.mark.asyncio
@patch("backend_v2.hooks.translation_hook.LLMClient.from_strategy", new_callable=AsyncMock)
async def test_translation_hook_role_segregation_and_success(
    mock_from_strategy: AsyncMock, mock_repository: AsyncMock
) -> None:
    """Ensures that the TranslationHook STRICTLY separates System and User roles."""
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={"target_locale": "fi", "fields_to_translate": ["title"]},
        global_context_vars={},
        inputs={"language": "fi", "title": "Example Title", "_private": "hidden"},
    )
    deps = HookDependencies(
        exec_repo=mock_repository,
        workflow_repo=mock_repository,
        comp_repo=mock_repository,
        identity_repo=mock_repository,
        audit_repo=mock_repository,
        system_repo=mock_repository,
    )  # noqa: E501

    # Setup Mock
    mock_client = AsyncMock()
    from backend_v2.models.dtos.state import TranslationResponseDTO

    mock_llm_response = TranslationResponseDTO(translated_data={"title": "Esimerkki Otsikko"})
    mock_client.run_structured_task.return_value = (mock_llm_response, {})
    mock_from_strategy.return_value = mock_client

    res = await cast(Awaitable[HookResult], translation_hook(state, deps))

    assert res.success is True
    assert res.state_delta is not None
    assert res.state_delta["title"] == "Esimerkki Otsikko"
    assert res.state_delta["_private"] == "hidden"  # Preserved field

    # Assert Role Segregation
    mock_from_strategy.assert_called_once_with("fast", repository=mock_repository)
    mock_client.run_structured_task.assert_called_once()

    call_kwargs = mock_client.run_structured_task.call_args.kwargs
    messages = call_kwargs["messages"]

    assert len(messages.static_messages) == 2
    assert messages.static_messages[0]["role"] == "system"
    assert "ROLE: You are an automatic JSON translator." in messages.static_messages[0]["content"]
    assert "suomeksi (Finnish)" in messages.static_messages[0]["content"]  # Embedded target language

    assert messages.static_messages[1]["role"] == "user"
    assert "source_data" in messages.static_messages[1]["content"]
    assert "Example Title" in messages.static_messages[1]["content"]


from pydantic import BaseModel

from backend_v2.hooks.translation_hook import translate_sdui_payload


class DummySduiModel(BaseModel):
    title: str
    items: list[dict[str, str]]


@pytest.mark.asyncio
async def test_translate_sdui_payload_success(mock_repository: AsyncMock) -> None:
    """Ensure it strictly passes through the payload per the No-String Mandate."""
    obj = DummySduiModel(
        title="Falsification",
        items=[{"label": "Coaching"}, {"status": "missing_context"}, {"unknown": "Not In Dict"}],  # noqa: E501
    )

    # Translate to Finnish
    res = await translate_sdui_payload(obj, "fi", mock_repository)

    assert isinstance(res, DummySduiModel)
    assert res.title == "Falsification"  # No String Mandate pass-through
    assert res.items[0]["label"] == "Coaching"
    assert res.items[1]["status"] == "missing_context"
    assert res.items[2]["unknown"] == "Not In Dict"


@pytest.mark.asyncio
async def test_translate_sdui_payload_skips_en(mock_repository: AsyncMock) -> None:
    """Ensure it skips translation for English."""
    obj = DummySduiModel(title="Falsification", items=[])
    res = await translate_sdui_payload(obj, "en", mock_repository)
    assert res.title == "Falsification"
    assert res is obj  # Returns same object reference
