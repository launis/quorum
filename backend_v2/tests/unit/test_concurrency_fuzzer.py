import asyncio
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.v2_core import I18nText, StepRule, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.settings import get_settings


@pytest.fixture(autouse=True)
def clear_litellm_provider_caches() -> Generator[None]:
    """Clear LiteLLM provider caches before and after each test."""
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

    def _mock_step_data() -> dict[str, Any]:
        return {
            "id": "stp_1234567890abcdef",
            "type": "llm",
            "model_strategy": "fast",
            "slug": "mock",
            "criteria_block_ids": ["blk_1234567890abcdef"],
            "extraction_protocol_block_id": "blk_1234567890abcdef",
            "name": {"default_locale": "en", "translations": {"en": "mock"}},
            "description": {"default_locale": "en", "translations": {"en": "mock"}},
        }

    repo.get_step_by_id.return_value = _mock_step_data()
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
    repo.get_workflow.return_value = _create_workflow(1).model_dump(mode="json")
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
    return compiler


def _create_workflow(num_steps: int) -> Workflow:
    return Workflow(
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_0000000000000000",
        slug="wf_fuzz",
        status="draft",
        version=1,
        default_profile_id="prof_0000000000000000",
        name=I18nText(default_locale="en", translations={"en": "Fuzz"}),
        description=I18nText(default_locale="en", translations={"en": "Fuzz"}),
        steps=[StepRule(id=f"step_{i:016x}", task_blueprint="bp_fuzz") for i in range(num_steps)],
    )


@pytest.mark.parametrize("concurrency", [1, 2, 5, 10, 50])
@pytest.mark.asyncio
async def test_concurrency_fuzzer_peak_limit(
    concurrency: int, mock_repo: AsyncMock, mock_compiler: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that DAGExecutor limits concurrent LLM requests to max_concurrent_llm_steps."""
    mock_settings = get_settings().model_copy(update={"max_concurrent_llm_steps": concurrency})
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

    workflow = _create_workflow(10)

    current_concurrent = 0
    peak_concurrent = 0
    lock = asyncio.Lock()

    async def mock_acompletion(*args: Any, **kwargs: Any) -> Any:
        nonlocal current_concurrent, peak_concurrent
        async with lock:
            current_concurrent += 1
            if current_concurrent > peak_concurrent:
                peak_concurrent = current_concurrent

        await asyncio.sleep(0.05)

        async with lock:
            current_concurrent -= 1

        class MockChoice:
            message = type("MockMessage", (), {"content": '{"atoms": []}', "tool_calls": []})
            finish_reason = "stop"

        return type(
            "MockResponse",
            (),
            {
                "choices": [MockChoice],
                "model": "mock-model",
                "usage": type("MockUsage", (), {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}),
            },
        )

    with patch("litellm.Router.acompletion", side_effect=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
            )

    assert peak_concurrent <= concurrency
    assert peak_concurrent > 0


@pytest.mark.asyncio
async def test_concurrency_fuzzer_zero_concurrency(
    mock_repo: AsyncMock, mock_compiler: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Boundary - Zero Concurrency: Should block forever, wait_for raises TimeoutError."""
    mock_settings = get_settings().model_copy(update={"max_concurrent_llm_steps": 0})
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

    workflow = _create_workflow(1)

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                executor.execute_workflow(
                    execution_id="exe_1111222233334444",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                ),
                timeout=0.2,
            )


@pytest.mark.asyncio
async def test_concurrency_fuzzer_exceeding_physical_limit(
    mock_repo: AsyncMock, mock_compiler: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Boundary - Exceeding Physical Limit: Large max_concurrent_llm_steps means no delay."""
    mock_settings = get_settings().model_copy(update={"max_concurrent_llm_steps": 100})
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

    workflow = _create_workflow(10)

    current_concurrent = 0
    peak_concurrent = 0
    lock = asyncio.Lock()

    async def mock_acompletion(*args: Any, **kwargs: Any) -> Any:
        nonlocal current_concurrent, peak_concurrent
        async with lock:
            current_concurrent += 1
            if current_concurrent > peak_concurrent:
                peak_concurrent = current_concurrent

        await asyncio.sleep(0.05)

        async with lock:
            current_concurrent -= 1

        class MockChoice:
            message = type("MockMessage", (), {"content": '{"atoms": []}', "tool_calls": []})
            finish_reason = "stop"

        return type(
            "MockResponse",
            (),
            {
                "choices": [MockChoice],
                "model": "mock-model",
                "usage": type("MockUsage", (), {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}),
            },
        )

    with patch("litellm.Router.acompletion", side_effect=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

            await asyncio.wait_for(
                executor.execute_workflow(
                    execution_id="exe_1111222233334444",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                ),
                timeout=5.0,
            )

    # With max=100 and 10 steps, they should all execute concurrently in one 0.05s window.
    # Therefore peak concurrent should equal the number of tasks.
    assert peak_concurrent == 10
