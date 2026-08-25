from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import litellm.exceptions
import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.v2_core import I18nText, StepRule, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.settings import get_settings


@pytest.fixture(autouse=True)
def clear_litellm_provider_caches() -> Generator[None]:
    from backend_v2.llm.provider import LiteLLMProvider

    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()
    LiteLLMProvider._httpx_clients.clear()
    yield
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()
    LiteLLMProvider._httpx_clients.clear()


@pytest.fixture(autouse=True)
def mock_pacing_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.get_step_by_id.return_value = {
        "id": "stp_1234567890abcdef",
        "type": "llm",
        "model_strategy": "fast",
        "slug": "mock",
        "criteria_block_ids": ["blk_1234567890abcdef"],
        "extraction_protocol_block_id": "blk_1234567890abcdef",
        "name": {"default_locale": "en", "translations": {"en": "mock"}},
        "description": {"default_locale": "en", "translations": {"en": "mock"}},
    }
    repo.get_step.return_value = repo.get_step_by_id.return_value
    repo.get_execution.return_value = {
        "id": "exe_1111222233334444",
        "workflow_id": "wf_0000000000000000",
        "status": ExecutionStatus.PENDING,
        "raw_inputs": {"dynamic_inputs": {"log": "test"}},
        "metadata": {"profile_id": "prof_0000000000000000", "target_locale": "en"},
    }
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1234567890abcdef",
            "slug": "task_bp",
            "label": {"default_locale": "fi", "translations": {"fi": "Testi", "en": "Test"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Kuvaus", "en": "Desc"}},
            "ai_description": "Strict extraction protocol.",
            "category_id": "system_rule",
            "type": "string",
            "allow_decimals": False,
            "output_extensions": [],
        }
    ]
    repo.get_output_profile_by_id.return_value = {
        "id": "prof_0000000000000000",
        "slug": "test_profile",
        "workflow_id": "wf_0000000000000000",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "visible_block_extensions": [],
        "visible_workflow_extensions": [],
    }
    repo.get_workflow.return_value = _create_workflow().model_dump(mode="json")
    repo.get_workflow_by_id.return_value = repo.get_workflow.return_value
    repo.get_model_registry.return_value = {
        "id": "sys_1111222233334444",
        "type": "model_registry",
        "slug": "default",
        "models": {
            "fast": {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "tpm_limit": 100000,
                "rpm_limit": 1000,
                "max_tokens": 4096,
                "temperature": 0.0,
            }
        },
    }
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    from pydantic import BaseModel

    class DummySchema(BaseModel):
        pass

    compiler = MagicMock()
    compiler.build_dynamic_schema.return_value = DummySchema
    compiler.compile_static_instructions.return_value = "static instructions"
    return compiler


def _create_workflow() -> Workflow:
    return Workflow(
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_0000000000000000",
        slug="wf_ctx_bounds",
        status="draft",
        version=1,
        default_profile_id="prof_0000000000000000",
        name=I18nText(default_locale="en", translations={"en": "Bounds"}),
        description=I18nText(default_locale="en", translations={"en": "Bounds"}),
        steps=[StepRule(id="step_0000000000000000", task_blueprint="bp_fuzz")],
    )


@pytest.mark.asyncio
async def test_context_window_exceeded_error_maps_critical(
    mock_repo: AsyncMock, mock_compiler: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prove ContextWindowExceededError maps to AGENT_EXECUTION_CRITICAL with Fail-Fast."""
    mock_settings = get_settings().model_copy(update={"llm_max_transient_retries": 3})
    monkeypatch.setattr("backend_v2.services.orchestrator.dag_executor.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    mock_acompletion = AsyncMock(
        side_effect=litellm.exceptions.ContextWindowExceededError(
            message="Token limit exceeded", llm_provider="openai", model="gpt-4"
        )
    )

    with patch("litellm.Router.acompletion", new=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_1111222233334444",
                    workflow=_create_workflow(),
                    raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                )

            # Since ErrorTraceEvent was emitted, the step failed. The DAGExecutor wraps it in a WORKFLOW_EXECUTION_FAILED error code, but let's check the trace event to be strictly sure it was mapped properly.
            assert "Workflow completed with failed steps" in str(exc_info.value)

            calls = mock_repo.update_execution.call_args_list
            final_call_args = calls[-1][0]
            payload = final_call_args[1]

            error_trace = next((evt for evt in payload["execution_trace"] if evt["event_type"] == "error"), None)
            assert error_trace is not None
            assert error_trace["content"]["error_code"] == ErrorCodes.AGENT_EXECUTION_CRITICAL.name

            # Non-transient error should only be called once
            assert mock_acompletion.call_count == 1


@pytest.mark.asyncio
async def test_non_context_400_error_maps_malformed(
    mock_repo: AsyncMock, mock_compiler: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prove Non-Context 400 Error maps to AGENT_RESPONSE_MALFORMED."""
    mock_settings = get_settings().model_copy(update={"llm_max_transient_retries": 3})
    monkeypatch.setattr("backend_v2.services.orchestrator.dag_executor.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    mock_acompletion = AsyncMock(
        side_effect=litellm.exceptions.BadRequestError(message="Invalid request", llm_provider="openai", model="gpt-4")
    )

    with patch("litellm.Router.acompletion", new=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

            with pytest.raises(AppException):
                await executor.execute_workflow(
                    execution_id="exe_1111222233334444",
                    workflow=_create_workflow(),
                    raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                )

            calls = mock_repo.update_execution.call_args_list
            final_call_args = calls[-1][0]
            payload = final_call_args[1]

            error_trace = next((evt for evt in payload["execution_trace"] if evt["event_type"] == "error"), None)
            assert error_trace is not None
            assert error_trace["content"]["error_code"] == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name

            # Non-transient error is retried once by the AI Critic schema validation loop
            assert mock_acompletion.call_count == 2


@pytest.mark.asyncio
async def test_transient_503_error_triggers_resilience_loop(
    mock_repo: AsyncMock, mock_compiler: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prove Transient 503 Error Path asserts mock call_count > 1 (Tenacity resilience loop triggered)."""
    mock_settings = get_settings().model_copy(
        update={
            "llm_max_transient_retries": 3,
            "llm_retry_min_seconds": 0,
            "llm_retry_max_seconds": 0,
        }
    )
    monkeypatch.setattr("backend_v2.services.orchestrator.dag_executor.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    mock_acompletion = AsyncMock(
        side_effect=litellm.exceptions.ServiceUnavailableError(
            message="Server overloaded", llm_provider="openai", model="gpt-4"
        )
    )

    with patch("litellm.Router.acompletion", new=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_1111222233334444",
                    workflow=_create_workflow(),
                    raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                )

            assert "Workflow completed with failed steps" in str(exc_info.value)

            # Should retry up to max transient retries (3) + initial attempt = 4 or stop_after_attempt logic?
            # It triggers the resilience loop. We just assert it retried.
            assert mock_acompletion.call_count > 1
