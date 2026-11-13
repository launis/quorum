"""Unit tests for Arq background worker lifecycle, DAG execution jobs, and profile synthesis tasks."""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import TypeAdapter, ValidationError

import backend_v2.worker as worker_mod
import backend_v2.workers.synthesis_worker as synthesis_worker_mod
from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.metadata import MetadataHookPayloadDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup, RenderedSynthesisCache
from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    DisplayScale,
    ExecutionStatus,
    HistoricalContextMode,
    LLMProvider,
    PromptBlockCategory,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    ExecutionStepFactory,
    MatrixPromptBlockFactory,
    OutputProfileFactory,
    SystemRulePromptBlockFactory,
    WorkflowFactory,
)
from backend_v2.tests.factories.model_factories import (
    TraceEventFactory as _TraceEventFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.tests.unit.test_worker_dlq_fallback import (
    test_generate_report_artifact_job_catches_service_unavailable_error,
)
from backend_v2.tests.unit.test_worker_synthesis import (
    test_worker_extracts_synthesis_from_trace,
    test_worker_synthesis_disabled_layout_omits_section_instruction,
    test_worker_synthesis_empty_sections_not_set_in_cache,
    test_worker_synthesis_executive_summary_instruction_and_cache,
    test_worker_synthesis_extracts_metrics_from_trace,
    test_worker_synthesis_malformed_metrics_remains_none,
    test_worker_synthesis_matrix_layout_directives,
    test_worker_synthesis_metrics_no_step_metadata,
    test_worker_synthesis_metrics_no_task_blueprint_in_metadata,
    test_worker_synthesis_missing_metrics_remains_none,
    test_worker_synthesis_multi_section_aggregation,
)
from backend_v2.worker import (
    WorkerSettings,
    health_check,
    shutdown,
    startup,
)
from backend_v2.workers import (
    VarianceExplanationResult,
    execute_workflow_job,
    generate_profile_synthesis_and_pdf_task,
    generate_report_artifact_job,
)

__all__ = [
    "test_generate_report_artifact_job_catches_service_unavailable_error",
    "test_worker_extracts_synthesis_from_trace",
    "test_worker_synthesis_disabled_layout_omits_section_instruction",
    "test_worker_synthesis_empty_sections_not_set_in_cache",
    "test_worker_synthesis_executive_summary_instruction_and_cache",
    "test_worker_synthesis_extracts_metrics_from_trace",
    "test_worker_synthesis_malformed_metrics_remains_none",
    "test_worker_synthesis_matrix_layout_directives",
    "test_worker_synthesis_metrics_no_step_metadata",
    "test_worker_synthesis_metrics_no_task_blueprint_in_metadata",
    "test_worker_synthesis_missing_metrics_remains_none",
    "test_worker_synthesis_multi_section_aggregation",
]

_DISTILLATION_ADAPTER: TypeAdapter[SynthesisDistillationDTO] = TypeAdapter(SynthesisDistillationDTO)
_CONTEXT_VARS_ADAPTER: TypeAdapter[ContextVariablesDTO] = TypeAdapter(ContextVariablesDTO)


class _ModelProfileFactory(ModelFactory[ModelProfile]):
    """Polyfactory model factory for deterministic ModelProfile configurations."""

    __model__ = ModelProfile
    __use_defaults__ = True


class _ModelRegistryFactory(ModelFactory[SystemConfigModelRegistry]):
    """Polyfactory model factory for deterministic SystemConfigModelRegistry instances."""

    __model__ = SystemConfigModelRegistry
    __use_defaults__ = True


class _RenderedSynthesisCacheFactory(ModelFactory[RenderedSynthesisCache]):
    """Polyfactory model factory for deterministic RenderedSynthesisCache instances."""

    __model__ = RenderedSynthesisCache
    __use_defaults__ = True


class _MetadataHookPayloadDTOFactory(ModelFactory[MetadataHookPayloadDTO]):
    """Polyfactory model factory for MetadataHookPayloadDTO instances."""

    __model__ = MetadataHookPayloadDTO
    __use_defaults__ = True


class _DeterministicWorkflowFactory(WorkflowFactory):
    """Workflow factory preserving Pydantic defaults on unset optional fields."""

    __use_defaults__ = True


class _DeterministicOutputProfileFactory(OutputProfileFactory):
    """OutputProfile factory preserving Pydantic defaults on unset optional fields."""

    __use_defaults__ = True


class _DeterministicExecutionRecordFactory(ExecutionRecordFactory):
    """ExecutionRecord factory preserving Pydantic defaults on unset optional fields."""

    __use_defaults__ = True


class _DeterministicExecutionStepFactory(ExecutionStepFactory):
    """ExecutionStep factory preserving Pydantic defaults on unset optional fields."""

    __use_defaults__ = True


def _empty_inputs() -> WorkflowInputs:
    """Return empty validated WorkflowInputs for worker entrypoint tests.

    Returns:
        Initialized WorkflowInputs container with empty dynamic_inputs.
    """
    return WorkflowInputs(dynamic_inputs={})


def _build_distillation_delta(
    distilled_inputs: str = "Data",
    include_matrix: bool = False,
    include_title: bool = False,
) -> HookDeltaDTO:
    """Build a typed HookDeltaDTO wrapping a SynthesisDistillationDTO payload.

    Args:
        distilled_inputs: Markdown summary string emitted by the distiller hook.
        include_matrix: Whether to populate a sample matrix item in matrices_to_explain.
        include_title: Whether to populate localized matrix title mapping.

    Returns:
        Configured HookDeltaDTO instance.
    """
    matrices = (
        [
            {
                "real_matrix_id": "blk_0195f3a0000070018111222233334444",
                "matrix_id": "m0",
                "matrix_label": "Target Matrix",
                "score": 85.0,
                "justification": "Evidence verified.",
            }
        ]
        if include_matrix
        else []
    )
    dto = _DISTILLATION_ADAPTER.validate_python(
        {
            "distilled_inputs": distilled_inputs,
            "matrices_to_explain": matrices,
            "target_locale": "fi",
            "title_map": {"blk_0195f3a0000070018111222233334444": "Kohdematriisi"} if include_title else {},
        },
        strict=False,
    )
    return HookDeltaDTO(delta=dto)


def _get_base_model_registry() -> SystemConfigModelRegistry:
    """Build the default test SystemConfigModelRegistry routed to mock_llm_99.

    Returns:
        Configured SystemConfigModelRegistry instance.
    """
    profile = _ModelProfileFactory.build(
        provider="mock_llm_99",
        model_name="gemini-2.5-pro",
        temperature=0.0,
        max_tokens=1024,
        is_active=True,
        tpm_limit=100000,
        rpm_limit=1000,
    )
    return _ModelRegistryFactory.build(
        id="mrg_0195f3a0000070018111222233334444",
        name="Default Test Registry",
        slug="model_registry",
        default_provider=LLMProvider.VERTEX_AI,
        tier_definitions={
            CognitiveTier.FAST: profile,
            CognitiveTier.BALANCED: profile,
            CognitiveTier.DEEP: profile,
            CognitiveTier.REASONING: profile,
        },
    )


def _get_base_workflow(strictness: int | None = 50, wf_id: str = "wf_0195f3a0000070018234567890123456") -> Workflow:
    """Build a baseline Workflow domain model for worker unit tests.

    Args:
        strictness: Default strictness level assigned to the workflow.
        wf_id: Canonical workflow Opaque Stripe ID.

    Returns:
        Configured Workflow instance.
    """
    return _DeterministicWorkflowFactory.build(
        id=wf_id,
        name=I18nText(translations={"en": "Test WF"}),
        slug="test-wf",
        description=I18nText(translations={"en": "desc"}),
        status="draft",
        version=1,
        steps=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prof_0195f3a0000070018111222233334444",
        model_registry_id="mrg_0195f3a0000070018111222233334444",
        default_strictness_level=strictness if strictness is not None else 50,
    )


def _get_minimal_profile(workflow_id: str = "wf_0195f3a0000070018234567890123456") -> OutputProfile:
    """Build a minimal OutputProfile without synthesis groups or extensions.

    Args:
        workflow_id: Parent workflow identifier.

    Returns:
        Configured OutputProfile instance.
    """
    return _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111222233334444",
        slug="prof-1",
        workflow_id=workflow_id,
        name=I18nText(translations={"en": "Profile 1"}),
        display_scale=DisplayScale.ORIGINAL,
        matrix_synthesis_groups=[],
        target_block_order=[],
    )


def _get_base_profile() -> OutputProfile:
    """Build a comprehensive OutputProfile with matrix groups and workflow extensions.

    Returns:
        Configured OutputProfile instance.
    """
    return _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111222233334444",
        slug="prof-1",
        workflow_id="wf_0195f3a0000070018234567890123456",
        name=I18nText(translations={"en": "Profile"}),
        synthesis_length_constraint=500,
        tone_instruction="Direct tone",
        executive_summary_directive="Synthesize executive summary.",
        matrix_1d_synthesis_directive="Synthesize 1D matrix metrics.",
        xai_synthesis_directive="Synthesize XAI highlights.",
        row_explanation_directive="Explain matrix row causality.",
        variance_synthesis_directive="Synthesize cognitive variance.",
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070018111111111111111",
                title=I18nText(translations={"en": "Matrix Section", "fi": "Matriisiosio"}),
                target_blocks=["blk_0195f3a0000070018111222233334444"],
            )
        ],
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
        visible_workflow_extensions=[
            XaiExtensionType.VARIANCE_VALIDATION,
            XaiExtensionType.AUTHENTICITY_EVALUATION,
        ],
        variance_target_block="blk_0195f3a0000070018111222233334444",
        max_extension_items=3,
    )


@pytest.fixture(autouse=True)
def mock_worker_report_service() -> Generator[MagicMock]:
    """Mock ReportService for background worker synthesis tasks.

    Yields:
        Mocked ReportService instance.
    """
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a0000070018234567890123456"
    mock_svc = MagicMock()
    mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
    mock_svc.compile_and_persist_artifact = AsyncMock()
    with (
        patch("backend_v2.workers.synthesis_worker.ReportService", return_value=mock_svc),
        patch("backend_v2.workers.synthesis_reducers.ReportService", return_value=mock_svc),
    ):
        yield mock_svc


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Verify health check task returns OK."""
    res = await health_check({})
    assert res == "OK"


@pytest.mark.asyncio
async def test_shutdown() -> None:
    """Verify shutdown lifecycle completes cleanly."""
    await shutdown({})


def test_worker_settings() -> None:
    """Verify WorkerSettings contains mandatory configuration and registered functions."""
    assert health_check in WorkerSettings.functions
    assert execute_workflow_job in WorkerSettings.functions
    assert generate_report_artifact_job in WorkerSettings.functions
    assert len(WorkerSettings.functions) == 3
    assert WorkerSettings.functions[0] is health_check
    assert WorkerSettings.functions[1] is execute_workflow_job
    assert WorkerSettings.functions[2] is generate_report_artifact_job
    assert WorkerSettings.on_startup == startup
    assert WorkerSettings.on_shutdown == shutdown


def test_variance_explanation_result() -> None:
    """Verify VarianceExplanationResult model validation and serialization."""
    dto = VarianceExplanationResult(explanation="Consistent alignment.")
    assert dto.explanation == "Consistent alignment."
    with pytest.raises(ValidationError):
        VarianceExplanationResult.model_validate({})


@pytest.mark.asyncio
async def test_startup() -> None:
    """Verify worker startup initializes repositories, telemetry, and execution engine dependencies."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    with (
        patch("backend_v2.worker.get_registered_uow_factory", return_value=MagicMock()),
        patch("backend_v2.worker.SecretService"),
        patch("backend_v2.worker.resolve_startup_logfire_token", new_callable=AsyncMock, return_value=None),
        patch("backend_v2.worker.configure_telemetry"),
        patch.object(worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch("backend_v2.worker.LLMClient"),
        patch("backend_v2.worker.PromptCompilerAdapter"),
        patch("backend_v2.worker.RAGPreflightService"),
        patch("backend_v2.worker.DAGExecutor"),
    ):
        ctx: dict[str, MagicMock | InMemoryUnifiedWorkflowRepository] = {}
        await startup(ctx)
        assert "engine" in ctx
        assert "repository" in ctx
        assert "llm_client" in ctx


@pytest.mark.asyncio
async def test_execute_workflow_job_not_found() -> None:
    """Verify missing workflow routes to DLQ and marks execution failed."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    mock_engine = AsyncMock()

    ctx = {"repository": mock_repo, "engine": mock_engine}

    res = await execute_workflow_job(ctx, "nonexistent", _empty_inputs())
    assert res.status == "FAILED/DLQ"


@pytest.mark.asyncio
async def test_execute_workflow_job_execution_missing_in_db() -> None:
    """Verify missing execution record in repository triggers Fail-Fast DLQ routing."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow())

    ctx = {"repository": mock_repo, "engine": AsyncMock()}
    res = await execute_workflow_job(
        ctx, "wf_0195f3a0000070018234567890123456", _empty_inputs(), execution_id="exe_missing"
    )
    assert res.status == "FAILED/DLQ"


@pytest.mark.asyncio
async def test_execute_workflow_job_missing_strictness_level() -> None:
    """Verify missing strictness level triggers Fail-Fast DLQ routing."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    wf = _get_base_workflow().model_copy(
        update={
            "default_profile_id": None,
            "default_strictness_level": None,
        }
    )
    await mock_repo.save_workflow(wf)
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            status=ExecutionStatus.PENDING,
            target_locale="en",
            metadata=ExecutionMetadata(),
            step_states={},
            output_profile_id=None,
        )
    )

    ctx = {"repository": mock_repo, "engine": AsyncMock()}
    res = await execute_workflow_job(
        ctx,
        "wf_0195f3a0000070018234567890123456",
        _empty_inputs(),
        execution_id="exe_0195f3a0000070018234567890123456",
    )
    assert res.status == "FAILED/DLQ"


@pytest.mark.asyncio
async def test_execute_workflow_job_missing_target_locale_raises_fail_fast() -> None:
    """Verify execute_workflow_job fails fast when target_locale is empty."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow(strictness=85))
    mock_repo.set_output_profiles([_get_minimal_profile()])
    rec = _DeterministicExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890123456",
        workflow_id="wf_0195f3a0000070018234567890123456",
        status=ExecutionStatus.PENDING,
        step_states={},
        target_locale="en",
        metadata=ExecutionMetadata(),
    ).model_copy(update={"target_locale": ""})
    await mock_repo.save_execution(rec)
    ctx = {"repository": mock_repo, "engine": AsyncMock(), "redis": None}

    res = await execute_workflow_job(
        ctx,
        "wf_0195f3a0000070018234567890123456",
        _empty_inputs(),
        execution_id="exe_0195f3a0000070018234567890123456",
    )
    assert res.status == "FAILED/DLQ"


@pytest.mark.asyncio
async def test_execute_workflow_job_cancelled() -> None:
    """Verify execute_workflow_job handles asyncio.CancelledError cleanly via DLQ."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow())
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.PENDING,
            target_locale="fi",
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.side_effect = asyncio.CancelledError()
    ctx = {"repository": mock_repo, "engine": mock_engine}
    res = await execute_workflow_job(
        ctx,
        "wf_0195f3a0000070018234567890123456",
        _empty_inputs(),
        execution_id="exe_0195f3a0000070018234567890123456",
    )
    assert res.status == "FAILED/DLQ"


@pytest.mark.asyncio
async def test_execute_workflow_job_failure_update_error() -> None:
    """Verify execute_workflow_job logs error when failure persistence update raises an exception."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    mock_repo.inject_fault("get_workflow", RuntimeError("Initial crash"))
    mock_repo.inject_fault("update_execution", RuntimeError("DB write crash"))
    try:
        ctx = {"repository": mock_repo, "engine": AsyncMock()}
        res = await execute_workflow_job(
            ctx,
            "wf_0195f3a0000070018234567890123456",
            _empty_inputs(),
            execution_id="exe_0195f3a0000070018234567890123456",
        )
        assert res.status == "FAILED/DLQ"
    finally:
        mock_repo.clear_faults()


@pytest.mark.asyncio
async def test_execute_workflow_job_cancelled_update_error() -> None:
    """Verify execute_workflow_job logs error when cancellation persistence update raises an exception."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow())
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.PENDING,
            target_locale="fi",
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    mock_repo.inject_fault("update_execution", RuntimeError("DB write crash"))
    try:
        mock_engine = AsyncMock()
        mock_engine.execute_workflow.side_effect = asyncio.CancelledError()
        ctx = {"repository": mock_repo, "engine": mock_engine}
        res = await execute_workflow_job(
            ctx,
            "wf_0195f3a0000070018234567890123456",
            _empty_inputs(),
            execution_id="exe_0195f3a0000070018234567890123456",
        )
        assert res.status == "FAILED/DLQ"
    finally:
        mock_repo.clear_faults()


@pytest.mark.asyncio
async def test_execute_workflow_job_success_with_metrics_and_no_redis() -> None:
    """Verify execute_workflow_job extracts trace metrics and updates status to PASSED without Redis."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_output_profiles([_get_minimal_profile()])
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.PENDING,
            target_locale="fi",
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )

    mock_trace: list[TraceEvent] = [
        _TraceEventFactory.build(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="error",
            step_name="step_err",
            content={"error": "Non-fatal warning"},
        ),
        _TraceEventFactory.build(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="output",
            step_name="step_synth",
            content={
                "_step_metadata": {
                    "token_usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cached_tokens": 20,
                        "reasoning_tokens": 10,
                        "cost_usd": 0.005,
                    },
                    "model_strategy": "synthesis",
                    "chunk_size": 2,
                }
            },
        ),
        _TraceEventFactory.build(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="output",
            step_name="step_no_usage",
            content={
                "_step_metadata": {
                    "token_usage": None,
                    "model_strategy": "fast",
                    "physical_model": "gemini-2.5-pro",
                    "system_fingerprint": "fp_test",
                    "chunk_size": 1,
                }
            },
        ),
    ]

    mock_exec_record = _DeterministicExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890123456",
        workflow_id="wf_0195f3a0000070018234567890123456",
        output_profile_id="prof_0195f3a0000070018111222233334444",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        steps=[
            _DeterministicExecutionStepFactory.build(
                id="step_other",
                label="Other step",
                status=ExecutionStatus.PASSED,
            )
        ],
        step_states={},
        execution_trace=mock_trace,
    )
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = mock_exec_record

    ctx = {"repository": mock_repo, "engine": mock_engine, "redis": None}

    res = await execute_workflow_job(
        ctx,
        workflow_id="wf_0195f3a0000070018234567890123456",
        inputs=_empty_inputs(),
        execution_id="exe_0195f3a0000070018234567890123456",
    )

    assert res.status == "COMPLETED"
    assert res.execution_id == "exe_0195f3a0000070018234567890123456"
    assert mock_repo.get_call_count("update_execution") >= 1
    updated_rec = await mock_repo.get_execution("exe_0195f3a0000070018234567890123456")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_not_found() -> None:
    """Verify generate_profile_synthesis_and_pdf_task exits cleanly when execution is absent."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task("exe_0195f3a0000070018234567890123456", "en")
        assert (await mock_repo.get_execution("exe_0195f3a0000070018234567890123456")) is None


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_missing_language() -> None:
    """Verify missing accept_language raises AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        await generate_profile_synthesis_and_pdf_task("exe_0195f3a0000070018234567890123456", None)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "accept_language" in exc_info.value.message


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_already_cached(
    mock_worker_report_service: MagicMock,
) -> None:
    """Verify generate_profile_synthesis_and_pdf_task invokes compile_and_persist_artifact when cached."""
    mock_redis = AsyncMock()
    mock_repo = InMemoryUnifiedWorkflowRepository()
    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        cached_entry = _RenderedSynthesisCacheFactory.build(
            section_syntheses={},
            row_explanations={},
            cited_sources=[],
            xai_highlights=[],
        )
        await mock_repo.save_execution(
            _DeterministicExecutionRecordFactory.build(
                id="exe_0195f3a0000070018234567890123456",
                workflow_id="wf_0195f3a0000070018234567890123456",
                output_profile_id="prof_0195f3a0000070018111222233334444",
                status=ExecutionStatus.RUNNING,
                target_locale="fi",
                metadata=ExecutionMetadata(),
                step_states={},
                profile_syntheses={"prof_0195f3a0000070018111222233334444": cached_entry},
            )
        )

        await generate_profile_synthesis_and_pdf_task(
            "exe_0195f3a0000070018234567890123456",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111222233334444",
            redis=mock_redis,
        )
        mock_worker_report_service.compile_and_persist_artifact.assert_called_once_with(
            "rep_0195f3a0000070018234567890123456",
            mock_redis,
        )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_succeeds_without_synthesis_block(
    mock_worker_report_service: MagicMock,
) -> None:
    """Verify synthesis succeeds with default system prompt when synthesis_block_id is omitted."""
    get_settings().use_mock_llm = True
    mock_redis = AsyncMock()
    mock_repo = InMemoryUnifiedWorkflowRepository()
    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await mock_repo.save_execution(
            _DeterministicExecutionRecordFactory.build(
                id="exe_0195f3a0000070018234567890123456",
                workflow_id="wf_0195f3a0000070018234567890123456",
                output_profile_id="prof_0195f3a0000070018111222233334444",
                status=ExecutionStatus.RUNNING,
                target_locale="fi",
                metadata=ExecutionMetadata(),
                step_states={},
                profile_syntheses={},
            )
        )
        mock_repo.set_output_profiles(
            [
                _DeterministicOutputProfileFactory.build(
                    id="prof_0195f3a0000070018111222233334444",
                    slug="prof-1",
                    workflow_id="wf_0195f3a0000070018234567890123456",
                    name=I18nText(translations={"en": "Profile"}),
                    synthesis_length_constraint=500,
                    matrix_synthesis_groups=[],
                    target_block_order=[],
                )
            ]
        )
        await mock_repo.save_workflow(_get_base_workflow(strictness=None))
        mock_repo.set_prompt_blocks([])
        mock_repo.set_model_registry(_get_base_model_registry())

        with patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook", new_callable=AsyncMock
        ) as mock_distiller:
            mock_distiller.return_value = HookResult(
                success=True,
                state_delta=_build_distillation_delta("Data"),
            )
            await generate_profile_synthesis_and_pdf_task(
                "exe_0195f3a0000070018234567890123456",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111222233334444",
                redis=mock_redis,
            )

            assert mock_repo.get_call_count("update_execution") >= 1
            mock_worker_report_service.compile_and_persist_artifact.assert_called_once_with(
                "rep_0195f3a0000070018234567890123456",
                mock_redis,
            )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_missing_max_extension_items() -> None:
    """Verify visible extensions with missing max_extension_items raises AppException."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await mock_repo.save_execution(
            _DeterministicExecutionRecordFactory.build(
                id="exe_0195f3a0000070018234567890123456",
                workflow_id="wf_0195f3a0000070018234567890123456",
                output_profile_id="prof_0195f3a0000070018111222233334444",
                status=ExecutionStatus.RUNNING,
                target_locale="fi",
                metadata=ExecutionMetadata(),
                step_states={},
                profile_syntheses={},
            )
        )
        base_prof = _DeterministicOutputProfileFactory.build(
            id="prof_0195f3a0000070018111222233334444",
            slug="prof-1",
            workflow_id="wf_0195f3a0000070018234567890123456",
            name=I18nText(translations={"en": "Profile"}),
            visible_workflow_extensions=[XaiExtensionType.AUTHENTICITY_EVALUATION],
            max_extension_items=3,
            matrix_synthesis_groups=[],
            target_block_order=[],
        )
        mock_repo.set_output_profiles([base_prof.model_copy(update={"max_extension_items": None})])
        mock_repo.set_prompt_blocks(
            [
                SystemRulePromptBlockFactory.build(
                    id="blk_0195f3a0000070018111222233334444",
                    slug="synth",
                    type=BlockDataType.INSTRUCTION,
                    label=I18nText(translations={"en": "Synth"}),
                    description=I18nText(translations={"en": "Desc"}),
                    instruction_text="Synthesize data.",
                    category_id=PromptBlockCategory.SYSTEM_RULE,
                )
            ]
        )
        await mock_repo.save_workflow(_get_base_workflow(strictness=None))

        with patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook", new_callable=AsyncMock
        ) as mock_distiller:
            mock_distiller.return_value = HookResult(
                success=True,
                state_delta=_build_distillation_delta("Data"),
            )
            with pytest.raises(AppException):
                await generate_profile_synthesis_and_pdf_task(
                    "exe_0195f3a0000070018234567890123456",
                    accept_language="fi",
                    profile_id="prof_0195f3a0000070018111222233334444",
                )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_full_execution_flow(
    mock_worker_report_service: MagicMock,
) -> None:
    """Verify complete end-to-end execution of generate_profile_synthesis_and_pdf_task."""
    get_settings().use_mock_llm = True
    mock_redis = AsyncMock()
    mock_repo = InMemoryUnifiedWorkflowRepository()

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        trace_event = _TraceEventFactory.build(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="output",
            step_name="step_perf",
            content={
                "_step_metadata": {"task_blueprint": "step_perf"},
                "blk_0195f3a0000070018111222233334444": {
                    "raw_score": 85.0,
                    "normalized_score": 85.0,
                    "level_breakdown": {"1.0": {"hits": 1, "total": 1}},
                },
            },
        )
        await mock_repo.save_execution(
            _DeterministicExecutionRecordFactory.build(
                id="exe_0195f3a0000070018234567890123456",
                workflow_id="wf_0195f3a0000070018234567890123456",
                output_profile_id="prof_0195f3a0000070018111222233334444",
                status=ExecutionStatus.RUNNING,
                target_locale="fi",
                metadata=ExecutionMetadata(),
                step_states={},
                profile_syntheses={},
                context_variables=_CONTEXT_VARS_ADAPTER.validate_python(
                    {
                        "variables": {
                            "step_linguistics": {
                                "performative_patterns": [
                                    {"pattern_id": "1", "detected_phrase": "phrase", "category": "cat"}
                                ],
                            }
                        }
                    },
                    strict=False,
                ),
                execution_trace=[trace_event],
            )
        )

        mock_repo.set_output_profiles([_get_base_profile()])

        mock_repo.set_prompt_blocks(
            [
                MatrixPromptBlockFactory.build(
                    id="blk_0195f3a0000070018111222233334444",
                    slug="target_1",
                    type=BlockDataType.FLOAT,
                    label=I18nText(translations={"en": "Target Matrix"}),
                    description=I18nText(translations={"en": "Desc"}),
                    category_id=PromptBlockCategory.MATRIX,
                    scales=[
                        MatrixScale(score=1, ai_label="L1", claims=[]),
                        MatrixScale(score=5, ai_label="L5", claims=[]),
                    ],
                )
            ]
        )
        mock_repo.set_model_registry(_get_base_model_registry())
        await mock_repo.save_workflow(_get_base_workflow())

        with patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook", new_callable=AsyncMock
        ) as mock_distiller:
            mock_distiller.return_value = HookResult(
                success=True,
                state_delta=_build_distillation_delta(
                    distilled_inputs="Sample analytical summary data.",
                    include_matrix=True,
                    include_title=True,
                ),
            )

            await generate_profile_synthesis_and_pdf_task(
                "exe_0195f3a0000070018234567890123456",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111222233334444",
                redis=mock_redis,
            )

            assert mock_repo.get_call_count("update_execution") >= 1
            mock_worker_report_service.compile_and_persist_artifact.assert_called_once_with(
                "rep_0195f3a0000070018234567890123456",
                mock_redis,
            )


@pytest.mark.asyncio
async def test_execute_workflow_job_with_redis_enqueues_render_job() -> None:
    """Verify execute_workflow_job completes without enqueuing legacy render jobs and marks PASSED."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow(strictness=85))
    mock_repo.set_output_profiles([_get_minimal_profile()])
    initial_exec = _DeterministicExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890123456",
        workflow_id="wf_0195f3a0000070018234567890123456",
        output_profile_id="prof_0195f3a0000070018111222233334444",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        step_states={},
        metadata=ExecutionMetadata(),
    )
    await mock_repo.save_execution(initial_exec)

    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = initial_exec

    mock_redis = AsyncMock()
    ctx = {"repository": mock_repo, "engine": mock_engine, "redis": mock_redis}

    res = await execute_workflow_job(
        ctx,
        workflow_id="wf_0195f3a0000070018234567890123456",
        inputs=_empty_inputs(),
        execution_id="exe_0195f3a0000070018234567890123456",
    )

    assert res.status == "COMPLETED"
    mock_redis.enqueue_job.assert_not_called()
    assert mock_repo.get_call_count("update_execution") >= 1
    updated_rec = await mock_repo.get_execution("exe_0195f3a0000070018234567890123456")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_dynamic_score_calculation() -> None:
    """Verify generate_profile_synthesis_and_pdf_task calculates dynamic matrix scores for step inputs."""
    get_settings().use_mock_llm = True
    mock_redis = AsyncMock()
    mock_repo = InMemoryUnifiedWorkflowRepository()

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        trace_event = _TraceEventFactory.build(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="output",
            step_name="sr_matrix_step",
            content={
                "blk_0195f3a0000070018111222233334444": {
                    "raw_score": 3.0,
                    "normalized_score": 50.0,
                    "level_breakdown": {
                        "1.0": {"hits": 1, "total": 2},
                        "5.0": {"hits": 1, "total": 2},
                    },
                    "atom_quotes": ["Evidence quote"],
                }
            },
        )
        await mock_repo.save_execution(
            _DeterministicExecutionRecordFactory.build(
                id="exe_0195f3a0000070018234567890123456",
                workflow_id="wf_0195f3a0000070018234567890123456",
                output_profile_id="prof_0195f3a0000070018111222233334444",
                status=ExecutionStatus.RUNNING,
                target_locale="fi",
                metadata=ExecutionMetadata(),
                step_states={},
                profile_syntheses={},
                context_variables=ContextVariablesDTO(variables={}),
                execution_trace=[trace_event],
            )
        )

        mock_repo.set_output_profiles([_get_minimal_profile()])
        await mock_repo.save_workflow(_get_base_workflow(strictness=85))

        typed_matrix = PromptBlockAdapter.validate_python(
            {
                "organization_id": "org_0195f3a0000070008000000000000001",
                "id": "blk_0195f3a0000070018111222233334444",
                "slug": "matrix_block",
                "type": "float",
                "label": {"translations": {"en": "Matrix"}},
                "description": {"translations": {"en": "Desc"}},
                "ai_description": "Evaluation instruction.",
                "category_id": "matrix",
                "scales": [
                    {
                        "score": 1,
                        "ai_label": "LOW",
                        "claims": [
                            {
                                "label": {"translations": {"en": "Low claim"}},
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_11112222333344445555666677778888",
                                        "concept_description": "Concept description for low claim.",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "ai_label": "HIGH",
                        "claims": [
                            {
                                "label": {"translations": {"en": "High claim"}},
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_22223333444455556666777788889999",
                                        "concept_description": "Concept description for high claim.",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        )
        mock_repo.set_prompt_blocks([typed_matrix])
        mock_repo.set_model_registry(_get_base_model_registry())

        with patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook", new_callable=AsyncMock
        ) as mock_distiller:
            mock_distiller.return_value = HookResult(
                success=True,
                state_delta=_build_distillation_delta("Sample summary data."),
            )

            await generate_profile_synthesis_and_pdf_task(
                "exe_0195f3a0000070018234567890123456",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111222233334444",
                redis=mock_redis,
            )

            assert mock_repo.get_call_count("update_execution") >= 1


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_database_failure_raises() -> None:
    """Verify repository fault during synthesis task propagates failure and cleans up faults."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    mock_repo.inject_fault("get_execution", RuntimeError("DB connection lost"))
    try:
        with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with pytest.raises(RuntimeError):
                await generate_profile_synthesis_and_pdf_task(
                    "exe_0195f3a0000070018234567890123456",
                    accept_language="fi",
                    profile_id="prof_0195f3a0000070018111222233334444",
                )
    finally:
        mock_repo.clear_faults()


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_missing_workflow_raises_app_exception() -> None:
    """Verify missing workflow in synthesis task raises Fail-Fast AppException."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    missing_wf_id = "wf_0195f3a0000070019999999999999999"
    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await mock_repo.save_execution(
            _DeterministicExecutionRecordFactory.build(
                id="exe_0195f3a0000070018234567890123456",
                workflow_id=missing_wf_id,
                output_profile_id="prof_0195f3a0000070018111222233334444",
                status=ExecutionStatus.RUNNING,
                target_locale="fi",
                metadata=ExecutionMetadata(),
                step_states={},
            )
        )
        mock_repo.set_output_profiles([_get_minimal_profile(workflow_id=missing_wf_id)])

        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                "exe_0195f3a0000070018234567890123456",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111222233334444",
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_starvation_short_circuit(
    mock_worker_report_service: MagicMock,
) -> None:
    """Verify data starvation in trace short-circuits synthesis and persists starvation cache."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        starvation_event = _TraceEventFactory.build(
            v=1,
            timestamp=datetime.now(UTC),
            step_name="synthesis_step",
            event_type="output",
            content={"event_type": "starvation", "total_atoms": 0, "reason": "No atoms"},
        )
        render_step = _DeterministicExecutionStepFactory.build(
            id="sys_render_prof_1",
            label="Rendering",
            status=ExecutionStatus.RUNNING,
        )
        await mock_repo.save_execution(
            _DeterministicExecutionRecordFactory.build(
                id="exe_0195f3a0000070018234567890123456",
                workflow_id="wf_0195f3a0000070018234567890123456",
                output_profile_id="prof_0195f3a0000070018111222233334444",
                status=ExecutionStatus.RUNNING,
                target_locale="en",
                execution_trace=[starvation_event],
                step_states={"sys_render_prof_1": render_step},
                metadata=ExecutionMetadata(),
            )
        )

        mock_redis = AsyncMock()
        await generate_profile_synthesis_and_pdf_task(
            "exe_0195f3a0000070018234567890123456",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111222233334444",
            redis=mock_redis,
        )

        assert mock_repo.get_call_count("update_execution") >= 1
        updated_exec = await mock_repo.get_execution("exe_0195f3a0000070018234567890123456")
        assert updated_exec is not None
        assert updated_exec.profile_syntheses is not None
        saved_cache = updated_exec.profile_syntheses["prof_0195f3a0000070018111222233334444"]
        assert saved_cache.data_starvation is not None
        assert saved_cache.data_starvation.event_type == "starvation"
        assert saved_cache.data_starvation.total_atoms == 0
        mock_worker_report_service.compile_and_persist_artifact.assert_called_once_with(
            "rep_0195f3a0000070018234567890123456",
            mock_redis,
        )


@pytest.mark.asyncio
async def test_execute_workflow_job_hydrates_offloaded_trace_telemetry() -> None:
    """Verify execute_workflow_job hydrates offloaded blob trace when in-memory trace lacks metadata."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_output_profiles([_get_minimal_profile()])
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.PENDING,
            target_locale="fi",
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )

    in_memory_trace: list[TraceEvent] = [
        _TraceEventFactory.build(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="progress",
            step_name="stp_preflight",
            content={"message": "running", "percentage": 50},
        )
    ]

    mock_exec_record = _DeterministicExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890123456",
        workflow_id="wf_0195f3a0000070018234567890123456",
        output_profile_id="prof_0195f3a0000070018111222233334444",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        step_states={
            "step_dag": _DeterministicExecutionStepFactory.build(
                id="step_dag",
                label="Step DAG",
                status=ExecutionStatus.PASSED,
            )
        },
        steps=[
            _DeterministicExecutionStepFactory.build(
                id="step_dag",
                label="Step DAG",
                status=ExecutionStatus.PENDING,
            )
        ],
        execution_trace=in_memory_trace,
        execution_trace_storage_path="executions/exe_0195f3a0000070018234567890123456/execution_trace.json",
    )
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = mock_exec_record

    offloaded_blob = (
        b'[{"v": 1, "step_name": "step_dag", "event_type": "output", "content": '
        b'{"step_metadata": {"model_strategy": "fast", "physical_model": "test_model", '
        b'"system_fingerprint": "fp_1", "chunk_size": 1, "token_usage": {"prompt_tokens": 500, '
        b'"completion_tokens": 100, "cached_tokens": 20, "reasoning_tokens": 10, "total_tokens": 600, '
        b'"cost_usd": 0.05}}}}]'
    )

    mock_storage = AsyncMock()
    mock_storage.read.return_value = offloaded_blob

    with patch("backend_v2.workers.execution_worker.get_storage_driver", return_value=mock_storage):
        ctx = {"repository": mock_repo, "engine": mock_engine, "redis": None}
        res = await execute_workflow_job(
            ctx,
            workflow_id="wf_0195f3a0000070018234567890123456",
            inputs=_empty_inputs(),
            execution_id="exe_0195f3a0000070018234567890123456",
            organization_id="org_test",
            user_id="usr_test",
        )

    assert res.status == "COMPLETED"
    mock_storage.read.assert_called_once_with("executions/exe_0195f3a0000070018234567890123456/execution_trace.json")

    assert mock_repo.get_call_count("update_execution") >= 1
    updated_rec = await mock_repo.get_execution("exe_0195f3a0000070018234567890123456")
    assert updated_rec is not None
    assert updated_rec.dag_cost_usd == 0.05
    assert updated_rec.prompt_tokens == 500
    assert updated_rec.completion_tokens == 100
    assert updated_rec.cached_tokens == 20
    assert updated_rec.reasoning_tokens == 10
    assert updated_rec.cost_estimate == 0.05
    assert updated_rec.models_used == {"fast": 600}
    assert len(updated_rec.steps) == 1
    assert updated_rec.steps[0].status == ExecutionStatus.PASSED
    assert updated_rec.steps[0].cost_usd == 0.05
    assert updated_rec.steps[0].prompt_tokens == 500


@pytest.mark.asyncio
async def test_generate_profile_synthesis_recovers_dag_cost_when_zero() -> None:
    """Verify synthesis task recovers DAG telemetry from offloaded blob when dag_cost_usd is zero."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_output_profiles([_get_minimal_profile()])
    mock_repo.set_prompt_blocks([])
    mock_repo.set_model_registry(_get_base_model_registry())
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="en",
            dag_cost_usd=0.0,
            cost_estimate=0.0,
            prompt_tokens=0,
            completion_tokens=0,
            cumulative_synthesis_cost=0.0,
            cumulative_synthesis_tokens=0,
            execution_trace=[],
            execution_trace_storage_path="executions/exe_0195f3a0000070018234567890123456/execution_trace.json",
            step_states={
                "sys_render_prof_1": _DeterministicExecutionStepFactory.build(
                    id="sys_render_prof_1",
                    label="Rendering",
                    status=ExecutionStatus.RUNNING,
                )
            },
            metadata=ExecutionMetadata(),
        )
    )

    offloaded_blob = (
        b'[{"v": 1, "step_name": "step_dag", "event_type": "output", "content": '
        b'{"step_metadata": {"model_strategy": "fast", "token_usage": {"prompt_tokens": 800, '
        b'"completion_tokens": 200, "cached_tokens": 50, "reasoning_tokens": 20, "total_tokens": 1070, '
        b'"cost_usd": 0.15}}}}, '
        b'{"v": 1, "step_name": "unrelated", "event_type": "output", "content": {"unrelated": 1}}]'
    )

    mock_storage = AsyncMock()
    mock_storage.read.return_value = offloaded_blob

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch("backend_v2.workers.synthesis_reducers.get_storage_driver", return_value=mock_storage),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=_build_distillation_delta("Data"),
                )
            ),
        ),
    ):
        mock_redis = AsyncMock()
        await generate_profile_synthesis_and_pdf_task(
            "exe_0195f3a0000070018234567890123456",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111222233334444",
            redis=mock_redis,
        )

    assert mock_storage.read.called
    assert mock_repo.get_call_count("update_execution") >= 1
    updated_exec = await mock_repo.get_execution("exe_0195f3a0000070018234567890123456")
    assert updated_exec is not None
    assert updated_exec.dag_cost_usd == 0.15
    assert updated_exec.prompt_tokens == 800
    assert updated_exec.completion_tokens == 200
    assert updated_exec.cached_tokens == 50
    assert updated_exec.reasoning_tokens == 20
    assert updated_exec.cost_estimate is not None
    assert updated_exec.cost_estimate >= 0.15


@pytest.mark.asyncio
async def test_generate_profile_synthesis_recovers_dag_cost_from_cost_estimate_fallback() -> None:
    """Verify DAG cost is recovered from cost_estimate minus cumulative_synthesis_cost when blob path is unset."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_output_profiles([_get_minimal_profile()])
    mock_repo.set_prompt_blocks([])
    mock_repo.set_model_registry(_get_base_model_registry())
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="en",
            dag_cost_usd=0.0,
            cost_estimate=1.25,
            prompt_tokens=0,
            completion_tokens=0,
            cumulative_synthesis_cost=0.25,
            cumulative_synthesis_tokens=100,
            execution_trace=[],
            execution_trace_storage_path=None,
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=_build_distillation_delta("Data"),
                )
            ),
        ),
    ):
        mock_redis = AsyncMock()
        await generate_profile_synthesis_and_pdf_task(
            "exe_0195f3a0000070018234567890123456",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111222233334444",
            redis=mock_redis,
        )

    assert mock_repo.get_call_count("update_execution") >= 1
    updated_exec = await mock_repo.get_execution("exe_0195f3a0000070018234567890123456")
    assert updated_exec is not None
    assert updated_exec.dag_cost_usd == 1.0
    assert updated_exec.cost_estimate is not None
    assert updated_exec.cost_estimate >= 1.0


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_matrix_directive_skips_group() -> None:
    """Verify missing matrix 1D directive skips matrix group synthesis cleanly."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="fi",
            execution_trace=[],
            execution_trace_storage_path=None,
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_model_registry(_get_base_model_registry())
    prof = _get_base_profile().model_copy(update={"matrix_1d_synthesis_directive": None})
    mock_repo.set_output_profiles([prof])

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=_build_distillation_delta(
                        distilled_inputs="Sample analytical summary data.",
                        include_matrix=True,
                    ),
                )
            ),
        ),
    ):
        await generate_profile_synthesis_and_pdf_task(
            "exe_0195f3a0000070018234567890123456",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111222233334444",
            redis=AsyncMock(),
        )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_xai_directive_skips_xai() -> None:
    """Verify missing XAI directive skips XAI highlight synthesis cleanly."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="fi",
            execution_trace=[],
            execution_trace_storage_path=None,
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_model_registry(_get_base_model_registry())
    prof = _get_base_profile().model_copy(update={"xai_synthesis_directive": None})
    mock_repo.set_output_profiles([prof])

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=_build_distillation_delta(
                        distilled_inputs="Sample analytical summary data.",
                        include_matrix=True,
                    ),
                )
            ),
        ),
    ):
        await generate_profile_synthesis_and_pdf_task(
            "exe_0195f3a0000070018234567890123456",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111222233334444",
            redis=AsyncMock(),
        )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_row_explanation_directive_skips_row_explanations() -> None:
    """Verify missing row explanation directive skips row explanation synthesis cleanly."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="fi",
            execution_trace=[],
            execution_trace_storage_path=None,
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_model_registry(_get_base_model_registry())
    prof = _get_base_profile().model_copy(
        update={
            "target_block_order": [
                TargetBlockType.MATRIX_GRAPHS_BLOCK,
                TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
            ],
            "row_explanation_directive": None,
        }
    )
    mock_repo.set_output_profiles([prof])

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=_build_distillation_delta(
                        distilled_inputs="Sample analytical summary data.",
                        include_matrix=True,
                    ),
                )
            ),
        ),
    ):
        await generate_profile_synthesis_and_pdf_task(
            "exe_0195f3a0000070018234567890123456",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111222233334444",
            redis=AsyncMock(),
        )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_state_delta_raises_app_exception() -> None:
    """Verify missing state_delta from distiller hook raises Fail-Fast AppException."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="fi",
            execution_trace=[],
            execution_trace_storage_path=None,
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_output_profiles([_get_base_profile()])

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(return_value=HookResult(success=True, state_delta=None)),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                "exe_0195f3a0000070018234567890123456",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111222233334444",
                redis=AsyncMock(),
            )
        assert "hook_result.state_delta cannot be None" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_distilled_inputs_raises_app_exception() -> None:
    """Verify non-distillation payload in state_delta raises Fail-Fast AppException."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="fi",
            execution_trace=[],
            execution_trace_storage_path=None,
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_output_profiles([_get_base_profile()])

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=_MetadataHookPayloadDTOFactory.build()),
                )
            ),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                "exe_0195f3a0000070018234567890123456",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111222233334444",
                redis=AsyncMock(),
            )
        assert "distilled_inputs missing from state_delta" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_profile_synthesis_no_profile_for_row_explanations_skips_gracefully() -> None:
    """Verify missing OutputProfile during profile synthesis raises ResourceNotFoundError."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(
        _DeterministicExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890123456",
            workflow_id="wf_0195f3a0000070018234567890123456",
            output_profile_id="prof_0195f3a0000070018111222233334444",
            status=ExecutionStatus.RUNNING,
            target_locale="fi",
            execution_trace=[],
            execution_trace_storage_path=None,
            step_states={},
            metadata=ExecutionMetadata(),
        )
    )
    await mock_repo.save_workflow(_get_base_workflow())
    mock_repo.set_model_registry(_get_base_model_registry())

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=_build_distillation_delta(
                        distilled_inputs="Sample analytical summary data.",
                        include_matrix=True,
                    ),
                )
            ),
        ),
    ):
        with pytest.raises(ResourceNotFoundError):
            await generate_profile_synthesis_and_pdf_task(
                "exe_0195f3a0000070018234567890123456",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111222233334444",
                redis=AsyncMock(),
            )


@pytest.mark.asyncio
async def test_worker_execution_persists_completed_record_in_memory_roundtrip() -> None:
    """Verify seeded workflow and execution record persist completed roundtrip in memory."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    workflow = _get_base_workflow()
    await mock_repo.save_workflow(workflow)
    mock_repo.set_output_profiles([_get_base_profile()])

    initial_record = _DeterministicExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890123456",
        workflow_id=workflow.id,
        output_profile_id="prof_0195f3a0000070018111222233334444",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        step_states={},
        metadata=ExecutionMetadata(),
    )
    await mock_repo.save_execution(initial_record)

    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = initial_record.model_copy(
        update={
            "status": ExecutionStatus.PASSED,
            "step_states": {
                "stp_0195f3a0000070018234567890123456": _DeterministicExecutionStepFactory.build(
                    id="stp_0195f3a0000070018234567890123456",
                    label="Step 1",
                    status=ExecutionStatus.PASSED,
                )
            },
        }
    )

    ctx = {"repository": mock_repo, "engine": mock_engine, "redis": None}
    res = await execute_workflow_job(
        ctx,
        workflow_id=workflow.id,
        inputs=_empty_inputs(),
        execution_id=initial_record.id,
    )
    assert res.status == "COMPLETED"

    reconstituted = await mock_repo.get_execution(initial_record.id)
    assert reconstituted is not None
    validated = ExecutionRecord.model_validate_json(reconstituted.model_dump_json())
    assert validated.status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_worker_handles_injected_repository_fault_and_clears_faults() -> None:
    """Verify injected repository fault routes failure to DLQ and clear_faults restores clean state."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    workflow = _get_base_workflow()
    await mock_repo.save_workflow(workflow)

    mock_repo.inject_fault("get_workflow", RuntimeError("Injected repository fault"))
    try:
        ctx = {"repository": mock_repo, "engine": AsyncMock()}
        res = await execute_workflow_job(
            ctx,
            workflow_id=workflow.id,
            inputs=_empty_inputs(),
            execution_id="exe_0195f3a0000070018234567890123456",
        )
        assert res.status == "FAILED/DLQ"
    finally:
        mock_repo.clear_faults()

    restored_wf = await mock_repo.get_workflow(workflow.id)
    assert restored_wf is not None
    assert restored_wf.id == workflow.id
