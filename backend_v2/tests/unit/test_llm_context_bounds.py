"""Unit tests for LLM context window, schema validation, and transient 503 error bounds."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.enums import (
    CognitiveTier,
    ExecutionStatus,
    HistoricalContextMode,
    LLMProvider,
    StepType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    OutputProfileFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class StepFactory(ModelFactory[Step]):
    """Polyfactory model factory for Step domain models."""

    __model__ = Step


class ModelProfileFactory(ModelFactory[ModelProfile]):
    """Polyfactory model factory for ModelProfile configurations."""

    __model__ = ModelProfile


class DummySchema(BaseModel):
    """Minimal schema stub returned by the mocked prompt compiler."""


@pytest.fixture(autouse=True)
def clear_litellm_provider_caches() -> Generator[None]:
    """Clear LiteLLM provider caches before and after each test.

    Yields:
        Control back to the active test case.
    """
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()
    LiteLLMProvider._httpx_clients.clear()
    yield
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()
    LiteLLMProvider._httpx_clients.clear()


@pytest.fixture(autouse=True)
def mock_pacing_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable provider pacing delays during unit test execution.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Create an in-memory unified repository seeded for LLM error bound tests.

    Returns:
        Seeded InMemoryUnifiedWorkflowRepository instance.
    """
    repo = InMemoryUnifiedWorkflowRepository()
    step = StepFactory.build(
        id="stp_0195f3a0000070018234567890abcdef",
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        slug="mock",
        criteria_block_ids=["blk_0195f3a0000070018234567890abcdef"],
        extraction_protocol_block_id="blk_0195f3a0000070018234567890abcdef",
        name=I18nText(translations={"en": "mock"}),
        description=I18nText(translations={"en": "mock"}),
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )
    repo._workflows._steps["stp_0195f3a0000070018234567890abcdef"] = step

    record = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018111222233334444",
        workflow_id="wf_0195f3a0000070008000000000000000",
        output_profile_id="prof_0195f3a0000070008000000000000000",
        status=ExecutionStatus.PENDING,
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
        metadata=ExecutionMetadata(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    repo._executions._save_isolated(record.id, record)

    raw_prompt_block = {
        "id": "blk_0195f3a0000070018234567890abcdef",
        "slug": "zero_trust_extraction_protocol",
        "label": {"translations": {"fi": "Testi", "en": "Test"}},
        "description": {"translations": {"fi": "Kuvaus", "en": "Desc"}},
        "instruction_text": "Strict extraction protocol.",
        "category_id": "system_rule",
        "type": "string",
        "allow_decimals": False,
        "output_extensions": [],
    }
    typed_block = PromptBlockAdapter.validate_python(raw_prompt_block)
    repo._prompt_blocks._save_isolated(typed_block.id, typed_block)

    profile = OutputProfileFactory.build(
        id="prof_0195f3a0000070008000000000000000",
        slug="test_profile",
        workflow_id="wf_0195f3a0000070008000000000000000",
        name=I18nText(translations={"en": "Test Profile"}),
        visible_block_extensions=[],
        visible_workflow_extensions=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008000000000000001",
                title=I18nText(translations={"en": "Default"}),
                target_blocks=["*"],
            )
        ],
    )
    repo._output_profiles._save_isolated(profile.id, profile)

    wf = _create_workflow()
    repo._workflows._save_isolated(wf.id, wf)

    tier_profile = ModelProfileFactory.build(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        tpm_limit=100000,
        rpm_limit=1000,
        max_tokens=4096,
        temperature=0.0,
        is_active=True,
        allowed_tools=[],
        additional_params={},
    )
    model_reg = SystemConfigModelRegistry(
        id="sys_0195f3a00000700e826807f3bfa3454d",
        type="model_registry",
        name="Default Model Registry",
        slug="default",
        default_provider=LLMProvider.OPENAI,
        tier_definitions={
            tier: tier_profile
            for tier in (
                CognitiveTier.FAST,
                CognitiveTier.BALANCED,
                CognitiveTier.DEEP,
                CognitiveTier.REASONING,
            )
        },
    )
    repo._system._model_registries.clear()
    repo._system._model_registries[model_reg.id] = model_reg
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    """Create a mocked prompt compiler returning DummySchema.

    Returns:
        Configured MagicMock prompt compiler.
    """
    compiler = MagicMock()
    compiler.build_dynamic_schema.return_value = DummySchema
    compiler.compile_static_instructions.return_value = "static instructions"
    return compiler


def _create_workflow() -> Workflow:
    """Create a single-step workflow for LLM context bound tests.

    Returns:
        Validated Workflow domain model.
    """
    return WorkflowFactory.build(
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        id="wf_0195f3a0000070008000000000000000",
        slug="wf_ctx_bounds",
        status="draft",
        version=1,
        default_profile_id="prof_0195f3a0000070008000000000000000",
        name=I18nText(translations={"en": "Bounds"}),
        description=I18nText(translations={"en": "Bounds"}),
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0195f3a0000070008000000000000000",
                task_blueprint="stp_0195f3a0000070018234567890abcdef",
                depends_on=[],
                input_mappings={},
            )
        ],
    )


@pytest.mark.asyncio
async def test_context_window_exceeded_error_maps_critical(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify ContextWindowExceededError maps to AGENT_EXECUTION_CRITICAL without transient retry.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    mock_settings = get_settings().model_copy(update={"llm_max_transient_retries": 3})
    monkeypatch.setattr("backend_v2.services.orchestrator.dag_executor.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    import litellm.exceptions

    mock_acompletion = AsyncMock(
        side_effect=litellm.exceptions.ContextWindowExceededError(
            message="Token limit exceeded",
            llm_provider="openai",
            model="gpt-4",
        )
    )

    with patch("litellm.Router.acompletion", new=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"log": "test"})),
                )
            )

            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_0195f3a0000070018111222233334444",
                    workflow=_create_workflow(),
                    raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
                )

            assert "AGENT_EXECUTION_CRITICAL" in str(exc_info.value)

            updated_record = await mock_repo.get_execution("exe_0195f3a0000070018111222233334444")
            assert updated_record is not None
            trace_list = updated_record.execution_trace
            error_trace = next(
                (evt for evt in trace_list if isinstance(evt, ErrorTraceEvent)),
                None,
            )
            assert error_trace is not None
            assert error_trace.error_code == ErrorCodes.AGENT_EXECUTION_CRITICAL.name
            assert mock_acompletion.call_count == 1


@pytest.mark.asyncio
async def test_non_context_400_error_maps_malformed(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify non-context BadRequestError triggers schema validation retry and maps failure code.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    mock_settings = get_settings().model_copy(update={"llm_max_transient_retries": 3, "llm_max_schema_retries": 1})
    monkeypatch.setattr("backend_v2.services.orchestrator.dag_executor.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.services.llm_task_executor.get_settings", lambda: mock_settings)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    import litellm.exceptions

    mock_acompletion = AsyncMock(
        side_effect=litellm.exceptions.BadRequestError(
            message="Invalid request",
            llm_provider="openai",
            model="gpt-4",
        )
    )

    with patch("litellm.Router.acompletion", new=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"log": "test"})),
                )
            )

            with pytest.raises(AppException):
                await executor.execute_workflow(
                    execution_id="exe_0195f3a0000070018111222233334444",
                    workflow=_create_workflow(),
                    raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
                )

            updated_record = await mock_repo.get_execution("exe_0195f3a0000070018111222233334444")
            assert updated_record is not None
            trace_list = updated_record.execution_trace
            error_trace = next(
                (evt for evt in trace_list if isinstance(evt, ErrorTraceEvent)),
                None,
            )
            assert error_trace is not None
            assert error_trace.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name
            assert mock_acompletion.call_count == 2


@pytest.mark.asyncio
async def test_transient_503_error_triggers_resilience_loop(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify transient ServiceUnavailableError triggers Tenacity retry loop before failing.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
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
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    import litellm.exceptions

    mock_acompletion = AsyncMock(
        side_effect=litellm.exceptions.ServiceUnavailableError(
            message="Server overloaded",
            llm_provider="openai",
            model="gpt-4",
        )
    )

    with patch("litellm.Router.acompletion", new=mock_acompletion):
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"log": "test"})),
                )
            )

            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_0195f3a0000070018111222233334444",
                    workflow=_create_workflow(),
                    raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
                )

            assert "unavailable" in str(exc_info.value).lower()
            assert mock_acompletion.call_count > 1
