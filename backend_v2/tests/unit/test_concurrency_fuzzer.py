import asyncio
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.system_config import SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.settings import Settings, get_settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


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


def _configure_repo_model_registry(repo: InMemoryUnifiedWorkflowRepository, rpm_limit: int = 1000) -> None:
    """Configure model registry on the mock repo with the specified rpm_limit."""
    model_reg = SystemConfigModelRegistry.model_validate(
        {
            "id": "sys_e26807f3bfa3454d",
            "name": "Default Stack",
            "tier_definitions": {
                tier: {
                    "provider": "openai",
                    "model_name": "gpt-4o-mini",
                    "tpm_limit": 100000,
                    "rpm_limit": rpm_limit,
                    "max_tokens": 4096,
                    "temperature": 0.0,
                }
                for tier in ("fast", "balanced", "deep", "reasoning")
            },
        }
    )
    repo.set_model_registry(model_reg)


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    repo = InMemoryUnifiedWorkflowRepository()

    def _mock_step_data():
        return {
            "id": "stp_1234567890abcdef",
            "type": "llm",
            "cognitive_tier": "fast",
            "slug": "mock",
            "criteria_block_ids": ["blk_1234567890abcdef"],
            "extraction_protocol_block_id": "blk_1234567890abcdef",
            "name": {"translations": {"en": "mock"}},
            "description": {"translations": {"en": "mock"}},
        }

    repo.set_step(_mock_step_data())
    repo.seed_raw_step("bp_fuzz", _mock_step_data())
    repo.set_execution(
        ExecutionRecord(
            id="exe_1111222233334444",
            workflow_id="wf_0000000000000000",
            output_profile_id="prof_0000000000000000",
            status=ExecutionStatus.PENDING,
            target_locale="en",
            raw_inputs={"dynamic_inputs": {"log": "test"}},
            metadata=ExecutionMetadata(),
        )
    )

    prompt_blocks = [
        PromptBlockAdapter.validate_python(
            {
                "id": "blk_1234567890abcdef",
                "slug": "zero_trust_extraction_protocol",
                "label": {"translations": {"fi": "Testi", "en": "Test"}},
                "description": {"translations": {"fi": "Kuvaus", "en": "Desc"}},
                "instruction_text": "Strict extraction protocol.",
                "category_id": "system_rule",
                "type": "string",
                "allow_decimals": False,
                "output_extensions": [],
            }
        )
    ]
    repo.set_prompt_blocks(prompt_blocks)
    repo.set_output_profiles(
        [
            {
                "id": "prof_0000000000000000",
                "slug": "test_profile",
                "workflow_id": "wf_0000000000000000",
                "name": {"translations": {"en": "Test Profile"}},
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0000000000000001",
                        "title": {"translations": {"en": "Default"}},
                        "target_blocks": ["*"],
                    }
                ],
            }
        ]
    )
    repo.set_workflow(_create_workflow(10))
    _configure_repo_model_registry(repo, rpm_limit=1000)
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


def _create_workflow(num_steps: int) -> Workflow:
    return Workflow(
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="sys_e26807f3bfa3454d",
        id="wf_0000000000000000",
        slug="wf_fuzz",
        status="draft",
        version=1,
        default_profile_id="prof_0000000000000000",
        name=I18nText(translations={"en": "Fuzz"}),
        description=I18nText(translations={"en": "Fuzz"}),
        steps=[StepRule(id=f"step_{i:016x}", task_blueprint="bp_fuzz") for i in range(num_steps)],
    )


async def _execute_and_measure_peak_concurrency(
    executor: DAGExecutor,
    workflow: Workflow,
) -> int:
    """Execute workflow while measuring peak concurrent LLM invocations."""
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
            mock_hooks.execute = AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(dynamic_inputs={"log": "test"})),
                )
            )

            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
            )

    return peak_concurrent


@pytest.mark.parametrize("concurrency", [1, 2, 5, 10])
@pytest.mark.asyncio
async def test_concurrency_fuzzer_peak_limit_stage_a(
    concurrency: int,
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stage A: Peak concurrency proven against provider SSOT across closed set [1, 2, 5, 10]."""
    _configure_repo_model_registry(mock_repo, rpm_limit=1000)
    mock_settings = get_settings().model_copy(
        update={"semaphore_max_concurrency": concurrency, "max_concurrent_llm_steps": 100}
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
    workflow = _create_workflow(10)

    peak_concurrent = await _execute_and_measure_peak_concurrency(executor, workflow)
    assert peak_concurrent <= concurrency
    assert peak_concurrent > 0


test_concurrency_fuzzer_peak_limit = test_concurrency_fuzzer_peak_limit_stage_a
test_concurrency_fuzzer_peak_limit_stage_b = test_concurrency_fuzzer_peak_limit_stage_a


@pytest.mark.asyncio
async def test_concurrency_fuzzer_low_rpm_limit_stage_a(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stage A: Peak concurrency proven against semaphore_low_rpm_limit under low rpm_limit=20."""
    _configure_repo_model_registry(mock_repo, rpm_limit=20)
    mock_settings = get_settings().model_copy(update={"semaphore_max_concurrency": 10, "max_concurrent_llm_steps": 100})
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

    peak_concurrent = await _execute_and_measure_peak_concurrency(executor, workflow)
    assert peak_concurrent <= mock_settings.semaphore_low_rpm_limit
    assert peak_concurrent > 0


def test_concurrency_settings_reject_zero_limits() -> None:
    """Verify Settings rejects semaphore_max_concurrency=0 via Pydantic ValidationError without bypass."""
    with pytest.raises(ValidationError):
        Settings(semaphore_max_concurrency=0)


@pytest.mark.parametrize("rpm_limit,expected_bound", [(30, 3), (20, 2)])
@pytest.mark.asyncio
async def test_concurrency_fuzzer_exceeding_physical_limit(
    rpm_limit: int,
    expected_bound: int,
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Boundary - Exceeding Physical Limit: Provider semaphore bounds execution under constrained RPM."""
    _configure_repo_model_registry(mock_repo, rpm_limit=rpm_limit)
    mock_settings = get_settings().model_copy(update={"semaphore_max_concurrency": 10, "max_concurrent_llm_steps": 100})
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

    peak_concurrent = await _execute_and_measure_peak_concurrency(executor, workflow)
    assert peak_concurrent <= expected_bound
    assert peak_concurrent > 0
