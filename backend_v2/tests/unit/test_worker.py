import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord
from backend_v2.settings import get_settings
from backend_v2.tests.unit.test_worker_dlq_fallback import (
    test_render_profile_job_catches_service_unavailable_error,
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
    VarianceExplanationResult,
    WorkerSettings,
    execute_workflow_job,
    generate_pdf_job,
    generate_pdf_task,
    generate_profile_synthesis_and_pdf_task,
    health_check,
    render_profile_job,
    shutdown,
    startup,
)

__all__ = [
    "test_render_profile_job_catches_service_unavailable_error",
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
    assert generate_pdf_job in WorkerSettings.functions
    assert render_profile_job in WorkerSettings.functions
    assert WorkerSettings.on_startup == startup
    assert WorkerSettings.on_shutdown == shutdown


def test_variance_explanation_result() -> None:
    """Verify VarianceExplanationResult model validation and serialization."""
    dto = VarianceExplanationResult.model_validate({"row_explanation": "Consistent alignment."})
    assert dto.row_explanation == "Consistent alignment."
    with pytest.raises(ValidationError):
        VarianceExplanationResult.model_validate({})


@pytest.mark.asyncio
async def test_startup() -> None:
    """Verify worker startup initializes repos, registries, and context dependencies."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            with patch("backend_v2.worker.LLMClient"):
                with patch("backend_v2.worker.PromptCompilerAdapter"):
                    with patch("backend_v2.worker.DAGExecutor"):
                        ctx: dict[str, Any] = {}
                        await startup(ctx)
                        assert "engine" in ctx
                        assert "repository" in ctx
                        assert "llm_client" in ctx


@pytest.mark.asyncio
async def test_execute_workflow_job_not_found() -> None:
    """Negative test: verify workflow not found routes to DLQ and marks failed."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = None

    mock_engine = AsyncMock()

    ctx: dict[str, Any] = {"repository": mock_repo, "engine": mock_engine}

    res = await execute_workflow_job(ctx, "nonexistent", {})
    assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_execute_workflow_job_execution_missing_in_db() -> None:
    """Negative test: verify missing execution record in DB triggers Fail-Fast."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1111222233334444",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 50,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_execution.return_value = None

    ctx: dict[str, Any] = {"repository": mock_repo, "engine": AsyncMock()}
    res = await execute_workflow_job(ctx, "wf_1234567890123456", {}, execution_id="exe_missing")
    assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_execute_workflow_job_missing_strictness_level() -> None:
    """Negative test: verify missing strictness level triggers Fail-Fast AppException."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": None,
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": None,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = None
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "status": "PENDING",
        "step_states": {},
        "output_profile_id": None,
    }

    ctx: dict[str, Any] = {"repository": mock_repo, "engine": AsyncMock()}
    res = await execute_workflow_job(ctx, "wf_1234567890123456", {}, execution_id="exe_1234567890123456")
    assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_execute_workflow_job_missing_target_locale_raises_fail_fast() -> None:
    """Verify execute_workflow_job fails fast when target_locale is missing in metadata."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "slug": "wf-1",
        "name": {"translations": {"en": "Workflow 1"}},
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1111222233334444",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 85,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111222233334444",
        "slug": "prof-1",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "status": "PENDING",
        "step_states": {},
        "metadata": {},  # Missing target_locale
    }
    ctx: dict[str, Any] = {"repository": mock_repo, "engine": AsyncMock(), "redis": None}

    res = await execute_workflow_job(ctx, "wf_1234567890123456", {}, execution_id="exe_1234567890123456")
    assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_execute_workflow_job_cancelled() -> None:
    """Verify execute_workflow_job handles asyncio.CancelledError gracefully."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.side_effect = asyncio.CancelledError()

    ctx: dict[str, Any] = {"repository": mock_repo, "engine": AsyncMock()}
    res = await execute_workflow_job(ctx, "wf_1234567890123456", {}, execution_id="exe_1234567890123456")
    assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_execute_workflow_job_success_with_metrics_and_no_redis() -> None:
    """Verify execute_workflow_job extracts trace metrics and updates status to PASSED when redis is absent."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1111222233334444",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 50,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111222233334444",
        "slug": "prof-1",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "PENDING",
        "target_locale": "fi",
        "step_states": {},
        "metadata": {},
    }

    mock_trace = [
        TraceEvent(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="error",
            step_name="step_err",
            content={"error": "Non-fatal warning"},
        ),
        TraceEvent(
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
    ]

    mock_exec_record = ExecutionRecord(
        id="exe_1234567890123456",
        workflow_id="wf_1234567890123456",
        output_profile_id="prof_1111222233334444",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        step_states={},
        execution_trace=mock_trace,
    )
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = mock_exec_record

    ctx: dict[str, Any] = {"repository": mock_repo, "engine": mock_engine, "redis": None}

    res = await execute_workflow_job(
        ctx,
        workflow_id="wf_1234567890123456",
        inputs={},
        execution_id="exe_1234567890123456",
    )

    assert res["status"] == "COMPLETED"
    assert res["execution_id"] == "exe_1234567890123456"
    mock_repo.update_execution.assert_called()


@pytest.mark.asyncio
async def test_generate_pdf_job_success() -> None:
    """Verify generate_pdf_job calls task and returns success string."""
    with patch("backend_v2.worker.generate_pdf_task", new_callable=AsyncMock) as mock_task:
        res = await generate_pdf_job({}, "exe_1234567890123456", "en-US", "prof_1111222233334444")
        assert res == "PDF Generated for exe_1234567890123456"
        mock_task.assert_called_once_with("exe_1234567890123456", "en-US", "prof_1111222233334444")


@pytest.mark.asyncio
async def test_generate_pdf_job_cancelled() -> None:
    """Negative test: verify generate_pdf_job returns DLQ dictionary on cancellation."""
    with patch("backend_v2.worker.generate_pdf_task", side_effect=asyncio.CancelledError):
        res = await generate_pdf_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_generate_pdf_job_exception() -> None:
    """Negative test: verify generate_pdf_job catches generic exception and routes to DLQ."""
    with patch("backend_v2.worker.generate_pdf_task", side_effect=RuntimeError("PDF engine crash")):
        res = await generate_pdf_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_render_profile_job_success() -> None:
    """Verify render_profile_job calls generate_profile_synthesis_and_pdf_task and returns success string."""
    with patch("backend_v2.worker.generate_profile_synthesis_and_pdf_task", new_callable=AsyncMock) as mock_task:
        ctx = {"redis": AsyncMock()}
        res = await render_profile_job(ctx, "exe_1234567890123456", "en-US", "prof_1111222233334444")
        assert res == "Render Job Completed for exe_1234567890123456"
        mock_task.assert_called_once_with("exe_1234567890123456", "en-US", "prof_1111222233334444", ctx["redis"])


@pytest.mark.asyncio
async def test_render_profile_job_cancelled() -> None:
    """Negative test: verify render_profile_job handles cancellation gracefully with DLQ."""
    with patch("backend_v2.worker.generate_profile_synthesis_and_pdf_task", side_effect=asyncio.CancelledError):
        res = await render_profile_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_render_profile_job_exception() -> None:
    """Negative test: verify render_profile_job routes generic exception to DLQ."""
    with patch("backend_v2.worker.generate_profile_synthesis_and_pdf_task", side_effect=ValueError("Invalid profile")):
        res = await render_profile_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_generate_pdf_task_execution_not_found() -> None:
    """Verify generate_pdf_task skips processing when execution does not exist in repo."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_execution.return_value = None

            await generate_pdf_task("exe_1234567890123456")
            mock_repo.get_execution.assert_called_once_with("exe_1234567890123456")


@pytest.mark.asyncio
async def test_generate_pdf_task_success_path() -> None:
    """Verify generate_pdf_task happy path: builds DTO, creates PDF, saves to storage, updates execution."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "fi",
                "metadata": {},
                "steps": [{"id": "sys_render_prof_1111222233334444", "label": "Rendering", "status": "RUNNING"}],
                "step_states": {
                    "sys_render_prof_1111222233334444": {
                        "id": "sys_render_prof_1111222233334444",
                        "label": "Rendering",
                        "status": "RUNNING",
                    }
                },
            }

            with patch("backend_v2.worker.BlueprintTransformer") as mock_transformer_class:
                mock_transformer = AsyncMock()
                mock_transformer_class.return_value = mock_transformer

                mock_dto = MagicMock()
                mock_dto.inner_sdui_blocks = []
                mock_transformer.build_report_dto.return_value = mock_dto

                with patch("backend_v2.worker.PdfReportService") as mock_pdf_class:
                    mock_pdf = AsyncMock()
                    mock_pdf_class.return_value = mock_pdf
                    mock_pdf.generate_execution_pdf.return_value = b"%PDF-1.4 sample"

                    with patch("backend_v2.worker.get_storage_driver") as mock_storage_class:
                        mock_storage = AsyncMock()
                        mock_storage_class.return_value = mock_storage
                        mock_storage.save.return_value = "executions/exe_1234567890123456/report.pdf"

                        await generate_pdf_task("exe_1234567890123456", None, "prof_1111222233334444")
                        mock_transformer.build_report_dto.assert_called_once_with(
                            "exe_1234567890123456", "prof_1111222233334444", "fi"
                        )
                        mock_storage.save.assert_called_once()
                        assert mock_repo.update_execution.call_count >= 1


@pytest.mark.asyncio
async def test_generate_pdf_task_exception_handling() -> None:
    """Negative test: verify generate_pdf_task catches failure and updates execution status to FAILED."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "en",
                "metadata": {},
                "steps": [{"id": "sys_render_prof_1111222233334444", "label": "Rendering", "status": "RUNNING"}],
                "step_states": {
                    "sys_render_prof_1111222233334444": {
                        "id": "sys_render_prof_1111222233334444",
                        "label": "Rendering",
                        "status": "RUNNING",
                    }
                },
            }

            with patch("backend_v2.worker.BlueprintTransformer", side_effect=RuntimeError("Transformer error")):
                with pytest.raises(RuntimeError):
                    await generate_pdf_task("exe_1234567890123456", "en", "prof_1111222233334444")
                assert mock_repo.update_execution.call_count >= 1


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_not_found() -> None:
    """Verify generate_profile_synthesis_and_pdf_task gracefully exits when execution missing."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_execution.return_value = None

            await generate_profile_synthesis_and_pdf_task("exe_1234567890123456", "en")
            mock_repo.get_execution.assert_called_once_with("exe_1234567890123456")


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_missing_language() -> None:
    """Negative test: verify missing accept_language raises AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        await generate_profile_synthesis_and_pdf_task("exe_1234567890123456", None)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "accept_language" in exc_info.value.message


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_already_cached() -> None:
    """Verify generate_profile_synthesis_and_pdf_task enqueues PDF job when synthesis is cached."""
    mock_redis = AsyncMock()
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "fi",
                "metadata": {},
                "step_states": {},
                "profile_syntheses": {
                    "prof_1111222233334444": {
                        "section_syntheses": {},
                        "row_explanations": {},
                        "cited_sources": [],
                        "xai_highlights": [],
                    }
                },
            }

            await generate_profile_synthesis_and_pdf_task(
                "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=mock_redis
            )
            mock_redis.enqueue_job.assert_called_once_with(
                "generate_pdf_job", "exe_1234567890123456", "fi", "prof_1111222233334444"
            )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_succeeds_without_synthesis_block() -> None:
    """Verify synthesis succeeds cleanly with default system prompt even when synthesis_block_id is omitted."""
    get_settings().use_mock_llm = True
    mock_redis = AsyncMock()
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "fi",
                "metadata": {},
                "step_states": {},
                "profile_syntheses": {},
            }
            mock_repo.get_output_profile_by_id.return_value = {
                "id": "prof_1111222233334444",
                "slug": "prof-1",
                "workflow_id": "wf_1234567890123456",
                "name": {"translations": {"en": "Profile"}},
                "synthesis_length_constraint": 500,
                "matrix_synthesis_groups": [],
                "target_block_order": [],
            }
            mock_repo.get_workflow_by_id.return_value = {
                "id": "wf_1234567890123456",
                "name": "Test WF",
                "slug": "test-wf",
                "description": "desc",
                "status": "draft",
                "version": 1,
                "steps": [],
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "default_profile_id": "prof_1111222233334444",
            }
            mock_repo.get_all_prompt_blocks.return_value = []
            mock_repo.get_model_registry.return_value = {
                "id": "cfg_1111111111111111",
                "type": "model_registry",
                "slug": "model_registry",
                "models": {
                    "synthesis": {
                        "provider": "mock_llm_99",
                        "model_name": "gemini-2.5-pro",
                        "temperature": 0.0,
                        "max_tokens": 1024,
                        "is_active": True,
                        "tpm_limit": 100000,
                        "rpm_limit": 1000,
                    }
                },
            }

            with patch("backend_v2.worker.synthesis_distiller_hook", new_callable=AsyncMock) as mock_distiller:
                mock_distiller.return_value = HookResult(
                    success=True, state_delta=HookDeltaDTO(delta={"distilled_inputs": "Data"})
                )
                await generate_profile_synthesis_and_pdf_task(
                    "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=mock_redis
                )

                assert mock_repo.update_execution.call_count >= 1
                mock_redis.enqueue_job.assert_called_once_with(
                    "generate_pdf_job", "exe_1234567890123456", "fi", "prof_1111222233334444"
                )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_missing_max_extension_items() -> None:
    """Negative test: verify visible extensions with missing max_extension_items triggers AppException."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "fi",
                "metadata": {},
                "step_states": {},
                "profile_syntheses": {},
            }
            mock_repo.get_output_profile_by_id.return_value = {
                "id": "prof_1111222233334444",
                "slug": "prof-1",
                "workflow_id": "wf_1234567890123456",
                "name": {"translations": {"en": "Profile"}},
                "visible_workflow_extensions": ["authenticity_evaluation"],
                "max_extension_items": None,
                "matrix_synthesis_groups": [],
                "target_block_order": [],
            }
            mock_repo.get_prompt_block.return_value = {
                "id": "blk_1111222233334444",
                "slug": "synth",
                "type": "instruction",
                "label": {"translations": {"en": "Synth"}},
                "description": {"translations": {"en": "Desc"}},
                "instruction_text": "Synthesize data.",
                "category_id": "system_rule",
            }
            mock_repo.get_workflow_by_id.return_value = {
                "id": "wf_1234567890123456",
                "name": "Test WF",
                "slug": "test-wf",
                "description": "desc",
                "status": "draft",
                "version": 1,
                "steps": [],
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "default_profile_id": "prof_1111222233334444",
            }
            mock_repo.get_all_prompt_blocks.return_value = []

            with patch("backend_v2.worker.synthesis_distiller_hook", new_callable=AsyncMock) as mock_distiller:
                mock_distiller.return_value = MagicMock(state_delta={"distilled_inputs": "Data"})
                with pytest.raises(AppException):
                    await generate_profile_synthesis_and_pdf_task(
                        "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444"
                    )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_full_execution_flow() -> None:
    """Verify complete end-to-end execution of generate_profile_synthesis_and_pdf_task with synthesis, row explanations, and variance."""
    get_settings().use_mock_llm = True
    mock_redis = AsyncMock()

    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "fi",
                "metadata": {},
                "step_states": {},
                "profile_syntheses": {},
                "context_variables": {
                    "step_linguistics": {
                        "performative_patterns": [{"pattern_id": "1", "detected_phrase": "phrase", "category": "cat"}],
                    }
                },
                "execution_trace": [
                    {
                        "v": 1,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "event_type": "output",
                        "step_name": "step_perf",
                        "content": {
                            "_step_metadata": {"task_blueprint": "step_perf"},
                            "blk_1111222233334444": {
                                "raw_score": 85.0,
                                "normalized_score": 85.0,
                                "level_breakdown": {"1.0": {"hits": 1, "total": 1}},
                            },
                        },
                    }
                ],
            }

            mock_repo.get_output_profile_by_id.return_value = {
                "id": "prof_1111222233334444",
                "slug": "prof-1",
                "workflow_id": "wf_1234567890123456",
                "name": {"translations": {"en": "Profile"}},
                "synthesis_length_constraint": 500,
                "tone_instruction": "Direct tone",
                "executive_summary_directive": "Synthesize executive summary.",
                "matrix_1d_synthesis_directive": "Synthesize 1D matrix metrics.",
                "xai_synthesis_directive": "Synthesize XAI highlights.",
                "row_explanation_directive": "Explain matrix row causality.",
                "variance_synthesis_directive": "Synthesize cognitive variance.",
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_1111111111111111",
                        "title": {
                            "translations": {"en": "Matrix Section", "fi": "Matriisiosio"},
                        },
                        "target_blocks": ["blk_1111222233334444"],
                    }
                ],
                "target_block_order": ["matrix_graphs_block"],
                "visible_workflow_extensions": ["variance_validation", "authenticity_evaluation"],
                "max_extension_items": 3,
                "performativity_detector_step_id": "step_perf",
            }

            async def mock_get_pb(pb_id: str) -> dict[str, Any] | None:
                return {
                    "id": pb_id,
                    "slug": f"slug_{pb_id}",
                    "type": "instruction",
                    "label": {"translations": {"en": "Label"}},
                    "description": {"translations": {"en": "Desc"}},
                    "instruction_text": f"Instruction for {pb_id}",
                    "category_id": "system_rule",
                }

            mock_repo.get_prompt_block.side_effect = mock_get_pb
            mock_repo.get_all_prompt_blocks.return_value = [
                {
                    "id": "blk_1111222233334444",
                    "slug": "target_1",
                    "type": "instruction",
                    "label": {"translations": {"en": "Target Matrix"}},
                    "description": {"translations": {"en": "Desc"}},
                    "instruction_text": "Target Matrix evaluation",
                    "category_id": "system_rule",
                }
            ]

            mock_repo.get_model_registry.return_value = {
                "id": "cfg_1111111111111111",
                "type": "model_registry",
                "slug": "model_registry",
                "models": {
                    "synthesis": {
                        "provider": "mock_llm_99",
                        "model_name": "gemini-2.5-pro",
                        "temperature": 0.0,
                        "max_tokens": 1024,
                        "is_active": True,
                        "tpm_limit": 100000,
                        "rpm_limit": 1000,
                    },
                    "strict": {
                        "provider": "mock_llm_99",
                        "model_name": "gemini-2.5-pro",
                        "temperature": 0.0,
                        "max_tokens": 1024,
                        "is_active": True,
                        "tpm_limit": 100000,
                        "rpm_limit": 1000,
                    },
                },
            }
            mock_repo.get_workflow_by_id.return_value = {
                "id": "wf_1234567890123456",
                "name": "Test WF",
                "slug": "test-wf",
                "description": "desc",
                "status": "draft",
                "version": 1,
                "steps": [],
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "default_profile_id": "prof_1111222233334444",
                "default_strictness_level": 50,
                "default_scoring_strategy": "AVERAGE",
            }

            with patch("backend_v2.worker.synthesis_distiller_hook", new_callable=AsyncMock) as mock_distiller:
                mock_distiller.return_value = HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(
                        delta={
                            "distilled_inputs": "Sample analytical summary data.",
                            "matrices_to_explain": [
                                {
                                    "real_matrix_id": "blk_1111222233334444",
                                    "matrix_id": "m0",
                                    "matrix_label": "Target Matrix",
                                    "score": 85.0,
                                    "justification": "Evidence verified.",
                                }
                            ],
                            "language": "fi",
                            "title_map": {"blk_1111222233334444": "Kohdematriisi"},
                        }
                    ),
                )

                await generate_profile_synthesis_and_pdf_task(
                    "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=mock_redis
                )

                mock_repo.update_execution.assert_called()
                mock_redis.enqueue_job.assert_called_once_with(
                    "generate_pdf_job", "exe_1234567890123456", "fi", "prof_1111222233334444"
                )


@pytest.mark.asyncio
async def test_execute_workflow_job_with_redis_enqueues_render_job() -> None:
    """Verify execute_workflow_job enqueues render_profile_job and updates status to RUNNING when redis is present."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1111222233334444",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 85,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111222233334444",
        "slug": "prof-1",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "PENDING",
        "target_locale": "fi",
        "step_states": {},
        "metadata": {},
    }

    mock_exec_record = ExecutionRecord(
        id="exe_1234567890123456",
        workflow_id="wf_1234567890123456",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        step_states={},
        output_profile_id="prof_1111222233334444",
    )
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = mock_exec_record

    mock_redis = AsyncMock()
    ctx: dict[str, Any] = {"repository": mock_repo, "engine": mock_engine, "redis": mock_redis}

    res = await execute_workflow_job(
        ctx,
        workflow_id="wf_1234567890123456",
        inputs={},
        execution_id="exe_1234567890123456",
    )

    assert res["status"] == "COMPLETED"
    mock_redis.enqueue_job.assert_called_once_with(
        "render_profile_job", "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444"
    )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_dynamic_score_calculation() -> None:
    """Verify generate_profile_synthesis_and_pdf_task calculates dynamic matrix scores for step inputs."""
    get_settings().use_mock_llm = True
    mock_redis = AsyncMock()

    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "fi",
                "metadata": {},
                "step_states": {},
                "profile_syntheses": {},
                "context_variables": {},
                "execution_trace": [
                    {
                        "v": 1,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "event_type": "output",
                        "step_name": "sr_matrix_step",
                        "content": {
                            "blk_1111222233334444": {
                                "raw_score": 3.0,
                                "normalized_score": 50.0,
                                "level_breakdown": {"1.0": {"hits": 1, "total": 2}, "5.0": {"hits": 1, "total": 2}},
                                "atom_quotes": ["Evidence quote"],
                            }
                        },
                    }
                ],
            }

            mock_repo.get_output_profile_by_id.return_value = {
                "id": "prof_1111222233334444",
                "slug": "prof-1",
                "workflow_id": "wf_1234567890123456",
                "name": {"translations": {"en": "Profile"}},
                "strictness_level": 85,
                "scoring_strategy": "AVERAGE",
                "display_scale": "original",
                "matrix_synthesis_groups": [],
                "target_block_order": [],
            }

            mock_repo.get_workflow_by_id.return_value = {
                "id": "wf_1234567890123456",
                "name": "Test WF",
                "slug": "test-wf",
                "description": "desc",
                "status": "draft",
                "version": 1,
                "steps": [],
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "default_profile_id": "prof_1111222233334444",
                "default_strictness_level": 85,
                "default_scoring_strategy": "AVERAGE",
            }

            mock_repo.get_all_prompt_blocks.return_value = [
                {
                    "id": "blk_1111222233334444",
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
            ]

            mock_repo.get_prompt_block.return_value = {
                "id": "blk_1111222233334444",
                "slug": "synth",
                "type": "instruction",
                "label": {"translations": {"en": "Synth"}},
                "description": {"translations": {"en": "Desc"}},
                "instruction_text": "Synthesize data.",
                "category_id": "system_rule",
            }

            mock_repo.get_model_registry.return_value = {
                "id": "cfg_1111111111111111",
                "type": "model_registry",
                "slug": "model_registry",
                "models": {
                    "synthesis": {
                        "provider": "mock_llm_99",
                        "model_name": "gemini-2.5-pro",
                        "temperature": 0.0,
                        "max_tokens": 1024,
                        "is_active": True,
                        "tpm_limit": 100000,
                        "rpm_limit": 1000,
                    }
                },
            }

            with patch("backend_v2.worker.synthesis_distiller_hook", new_callable=AsyncMock) as mock_distiller:
                mock_distiller.return_value = HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(
                        delta={
                            "distilled_inputs": "Sample summary data.",
                            "matrices_to_explain": [],
                        }
                    ),
                )

                await generate_profile_synthesis_and_pdf_task(
                    "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=mock_redis
                )

                mock_repo.update_execution.assert_called()


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_database_failure_raises() -> None:
    """Negative test: verify database update failure in synthesis task raises AppException."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.side_effect = RuntimeError("DB connection lost")

            with pytest.raises(RuntimeError):
                await generate_profile_synthesis_and_pdf_task(
                    "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444"
                )


@pytest.mark.asyncio
async def test_generate_pdf_task_app_exception_handling() -> None:
    """Negative test: verify generate_pdf_task catches AppException and re-raises with execution update."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "en",
                "metadata": {},
                "step_states": {
                    "sys_render_prof_1": {"id": "sys_render_prof_1", "label": "Rendering", "status": "RUNNING"}
                },
            }

            with patch("backend_v2.worker.BlueprintTransformer") as mock_transformer_class:
                mock_transformer = AsyncMock()
                mock_transformer_class.return_value = mock_transformer
                mock_transformer.build_report_dto.side_effect = AppException(
                    message="Blueprint render error",
                    status_code=500,
                    details={"error_code": ErrorCodes.PDF_GENERATION_FAILED.value},
                )

                with pytest.raises(AppException):
                    await generate_pdf_task("exe_1234567890123456", "en", "prof_1111222233334444")
                assert mock_repo.update_execution.call_count >= 1


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_starvation_short_circuit() -> None:
    """Tests that data starvation in trace short-circuits synthesis and saves starvation cache."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "en",
                "execution_trace": [
                    {
                        "step_name": "synthesis_step",
                        "event_type": "output",
                        "content": {"event_type": "starvation", "total_atoms": 0, "reason": "No atoms"},
                    }
                ],
                "step_states": {
                    "sys_render_prof_1": {"id": "sys_render_prof_1", "label": "Rendering", "status": "RUNNING"}
                },
                "metadata": {},
            }

            mock_redis = AsyncMock()
            await generate_profile_synthesis_and_pdf_task(
                "exe_1234567890123456", accept_language="en", profile_id="prof_1111222233334444", redis=mock_redis
            )

            assert mock_repo.update_execution.call_count >= 1
            calls_with_syntheses = [
                call[0][1]
                for call in mock_repo.update_execution.call_args_list
                if (hasattr(call[0][1], "profile_syntheses") and call[0][1].profile_syntheses is not None)
                or (isinstance(call[0][1], dict) and "profile_syntheses" in call[0][1])
            ]
            assert len(calls_with_syntheses) == 1
            call_payload = calls_with_syntheses[0]
            ps = getattr(call_payload, "profile_syntheses", None) or call_payload.get("profile_syntheses")
            saved_cache = ps["prof_1111222233334444"]
            starvation = getattr(saved_cache, "data_starvation", None) or (
                saved_cache.get("data_starvation") if isinstance(saved_cache, dict) else None
            )
            ev_type = getattr(starvation, "event_type", None) or (
                starvation.get("event_type") if isinstance(starvation, dict) else None
            )
            total_atoms = (
                getattr(starvation, "total_atoms", None)
                if getattr(starvation, "total_atoms", None) is not None
                else (starvation.get("total_atoms") if isinstance(starvation, dict) else None)
            )
            assert ev_type == "starvation"
            assert total_atoms == 0
            mock_redis.enqueue_job.assert_called_once_with(
                "generate_pdf_job", "exe_1234567890123456", "en", "prof_1111222233334444"
            )


@pytest.mark.asyncio
async def test_execute_workflow_job_hydrates_offloaded_trace_telemetry() -> None:
    """Verify execute_workflow_job hydrates offloaded trace when in-memory trace lacks metadata."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1111222233334444",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 50,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111222233334444",
        "slug": "prof-1",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "PENDING",
        "target_locale": "fi",
        "step_states": {},
        "metadata": {},
    }

    in_memory_trace = [
        TraceEvent(
            v=1,
            timestamp=datetime.now(UTC),
            event_type="progress",
            step_name="stp_preflight",
            content={"message": "running", "percentage": 50},
        )
    ]

    mock_exec_record = ExecutionRecord(
        id="exe_1234567890123456",
        workflow_id="wf_1234567890123456",
        output_profile_id="prof_1111222233334444",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        step_states={
            "step_dag": {
                "id": "step_dag",
                "label": "Step DAG",
                "status": ExecutionStatus.PASSED,
            }
        },
        steps=[
            {
                "id": "step_dag",
                "label": "Step DAG",
                "status": ExecutionStatus.PENDING,
            }
        ],
        execution_trace=in_memory_trace,
        execution_trace_storage_path="executions/exe_1234567890123456/execution_trace.json",
    )
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = mock_exec_record

    offloaded_blob = (
        b'[{"v": 1, "step_name": "step_dag", "event_type": "output", "content": '
        b'{"_step_metadata": {"model_strategy": "fast", "physical_model": "test_model", '
        b'"system_fingerprint": "fp_1", "chunk_size": 1, "token_usage": {"prompt_tokens": 500, '
        b'"completion_tokens": 100, "cached_tokens": 20, "reasoning_tokens": 10, "total_tokens": 600, '
        b'"cost_usd": 0.05}}}}]'
    )

    mock_storage = AsyncMock()
    mock_storage.read.return_value = offloaded_blob

    with patch("backend_v2.worker.get_storage_driver", return_value=mock_storage):
        ctx: dict[str, Any] = {"repository": mock_repo, "engine": mock_engine, "redis": None}
        res = await execute_workflow_job(
            ctx,
            workflow_id="wf_1234567890123456",
            inputs={},
            execution_id="exe_1234567890123456",
            organization_id="org_test",
            user_id="usr_test",
        )

    assert res["status"] == "COMPLETED"
    mock_storage.read.assert_called_once_with("executions/exe_1234567890123456/execution_trace.json")

    update_call = mock_repo.update_execution.call_args[0][1]
    assert update_call.dag_cost_usd == 0.05
    assert update_call.prompt_tokens == 500
    assert update_call.completion_tokens == 100
    assert update_call.cached_tokens == 20
    assert update_call.reasoning_tokens == 10
    assert update_call.cost_estimate == 0.05
    assert update_call.models_used == {"fast": 600}
    assert len(update_call.steps) == 1
    assert update_call.steps[0].status == ExecutionStatus.PASSED
    assert update_call.steps[0].cost_usd == 0.05
    assert update_call.steps[0].prompt_tokens == 500


@pytest.mark.asyncio
async def test_generate_profile_synthesis_recovers_dag_cost_when_zero() -> None:
    """Verify render_profile_job recovers DAG telemetry from blob if dag_cost_usd is 0."""
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1111222233334444",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 50,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111222233334444",
        "slug": "prof-1",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }
    mock_repo.get_all_prompt_blocks.return_value = []
    mock_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_profile_id": "prof_1111222233334444",
    }
    mock_repo.get_model_registry.return_value = {
        "id": "cfg_1111111111111111",
        "type": "model_registry",
        "slug": "model_registry",
        "models": {
            "synthesis": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            }
        },
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "en",
        "dag_cost_usd": 0.0,
        "cost_estimate": 0.0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cumulative_synthesis_cost": 0.0,
        "cumulative_synthesis_tokens": 0,
        "execution_trace": [],
        "execution_trace_storage_path": "executions/exe_1234567890123456/execution_trace.json",
        "step_states": {"sys_render_prof_1": {"id": "sys_render_prof_1", "label": "Rendering", "status": "RUNNING"}},
        "metadata": {},
    }

    offloaded_blob = (
        b'[{"v": 1, "step_name": "step_dag", "event_type": "output", "content": '
        b'{"_step_metadata": {"model_strategy": "fast", "token_usage": {"prompt_tokens": 800, '
        b'"completion_tokens": 200, "cached_tokens": 50, "reasoning_tokens": 20, "total_tokens": 1070, '
        b'"cost_usd": 0.15}}}}, '
        b'{"v": 1, "step_name": "unrelated", "event_type": "output", "content": {"unrelated": 1}}]'
    )

    mock_storage = AsyncMock()
    mock_storage.read.return_value = offloaded_blob

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch("backend_v2.worker.get_storage_driver", return_value=mock_storage),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"distilled_inputs": "Data"}))
            ),
        ),
    ):
        mock_redis = AsyncMock()
        await generate_profile_synthesis_and_pdf_task(
            "exe_1234567890123456", accept_language="en", profile_id="prof_1111222233334444", redis=mock_redis
        )

    assert mock_storage.read.called
    update_calls = [
        call[0][1]
        for call in mock_repo.update_execution.call_args_list
        if hasattr(call[0][1], "profile_syntheses") and call[0][1].profile_syntheses is not None
    ]
    assert len(update_calls) == 1
    call_payload = update_calls[0]
    assert call_payload.dag_cost_usd == 0.15
    assert call_payload.prompt_tokens == 800
    assert call_payload.completion_tokens == 200
    assert call_payload.cached_tokens == 50
    assert call_payload.reasoning_tokens == 20
    assert call_payload.cost_estimate >= 0.15


@pytest.mark.asyncio
async def test_job_wrappers_call_tasks() -> None:
    """Verify render_profile_job and generate_pdf_job invoke underlying tasks."""
    with (
        patch("backend_v2.worker.generate_profile_synthesis_and_pdf_task", AsyncMock()) as mock_synth,
        patch("backend_v2.worker.generate_pdf_task", AsyncMock()) as mock_pdf,
    ):
        ctx: dict[str, Any] = {"redis": None}
        r1 = await render_profile_job(ctx, "exe_123", accept_language="fi", profile_id="prof_1")
        assert "Completed" in str(r1)
        mock_synth.assert_called_once_with("exe_123", "fi", "prof_1", None)

        r2 = await generate_pdf_job(ctx, "exe_123", accept_language="fi", profile_id="prof_1")
        assert "PDF Generated" in str(r2)
        mock_pdf.assert_called_once_with("exe_123", "fi", "prof_1")


@pytest.mark.asyncio
async def test_generate_profile_synthesis_recovers_dag_cost_from_cost_estimate_fallback() -> None:
    """Verify DAG cost is recovered from cost_estimate - prev_cost when storage path is missing."""
    get_settings().use_mock_llm = True
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1111222233334444",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 50,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111222233334444",
        "slug": "prof-1",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }
    mock_repo.get_all_prompt_blocks.return_value = []
    mock_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_profile_id": "prof_1111222233334444",
    }
    mock_repo.get_model_registry.return_value = {
        "id": "cfg_1111111111111111",
        "type": "model_registry",
        "slug": "model_registry",
        "models": {
            "synthesis": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            }
        },
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "en",
        "dag_cost_usd": 0.0,
        "cost_estimate": 1.25,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cumulative_synthesis_cost": 0.25,
        "cumulative_synthesis_tokens": 100,
        "execution_trace": [],
        "execution_trace_storage_path": None,
        "step_states": {},
        "metadata": {},
    }

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"distilled_inputs": "Data"}))
            ),
        ),
    ):
        mock_redis = AsyncMock()
        await generate_profile_synthesis_and_pdf_task(
            "exe_1234567890123456", accept_language="en", profile_id="prof_1111222233334444", redis=mock_redis
        )

    update_calls = [
        call[0][1]
        for call in mock_repo.update_execution.call_args_list
        if hasattr(call[0][1], "profile_syntheses") and call[0][1].profile_syntheses is not None
    ]
    assert len(update_calls) == 1
    call_payload = update_calls[0]
    assert call_payload.dag_cost_usd == 1.0
    assert call_payload.cost_estimate >= 1.0


def _get_base_model_registry_dict() -> dict[str, Any]:
    return {
        "id": "cfg_1111111111111111",
        "type": "model_registry",
        "slug": "model_registry",
        "models": {
            "synthesis": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            },
            "strict": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            },
        },
    }


def _get_base_workflow_dict() -> dict[str, Any]:
    return {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_profile_id": "prof_1111222233334444",
        "default_strictness_level": 50,
        "default_scoring_strategy": "AVERAGE",
    }


def _get_base_profile_dict() -> dict[str, Any]:
    return {
        "id": "prof_1111222233334444",
        "slug": "prof-1",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Profile"}},
        "synthesis_length_constraint": 500,
        "tone_instruction": "Direct tone",
        "executive_summary_directive": "Synthesize executive summary.",
        "matrix_1d_synthesis_directive": "Synthesize 1D matrix metrics.",
        "xai_synthesis_directive": "Synthesize XAI highlights.",
        "row_explanation_directive": "Explain matrix row causality.",
        "variance_synthesis_directive": "Synthesize cognitive variance.",
        "matrix_synthesis_groups": [
            {
                "id": "grp_1111111111111111",
                "title": {"translations": {"en": "Matrix Section", "fi": "Matriisiosio"}},
                "target_blocks": ["blk_1111222233334444"],
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
        "visible_workflow_extensions": ["variance_validation", "authenticity_evaluation"],
        "max_extension_items": 3,
        "performativity_detector_step_id": "step_perf",
    }


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_matrix_directive_skips_group() -> None:
    """Positive: Verify missing matrix synthesis directive skips group synthesis gracefully with a warning."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "fi",
        "execution_trace": [],
        "execution_trace_storage_path": None,
        "step_states": {},
        "metadata": {},
    }
    mock_repo.get_workflow_by_id.return_value = _get_base_workflow_dict()
    mock_repo.get_model_registry.return_value = _get_base_model_registry_dict()
    prof_dict = _get_base_profile_dict()
    prof_dict["matrix_1d_synthesis_directive"] = None
    mock_repo.get_output_profile_by_id.return_value = prof_dict

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(
                        delta={
                            "distilled_inputs": "Sample analytical summary data.",
                            "matrices_to_explain": [],
                            "language": "fi",
                            "title_map": {},
                        }
                    ),
                )
            ),
        ),
    ):
        await generate_profile_synthesis_and_pdf_task(
            "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=AsyncMock()
        )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_xai_directive_skips_xai() -> None:
    """Positive: Verify missing XAI synthesis directive skips XAI synthesis gracefully with a warning."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "fi",
        "execution_trace": [],
        "execution_trace_storage_path": None,
        "step_states": {},
        "metadata": {},
    }
    mock_repo.get_workflow_by_id.return_value = _get_base_workflow_dict()
    mock_repo.get_model_registry.return_value = _get_base_model_registry_dict()
    prof_dict = _get_base_profile_dict()
    prof_dict["xai_synthesis_directive"] = None
    mock_repo.get_output_profile_by_id.return_value = prof_dict

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(
                        delta={
                            "distilled_inputs": "Sample analytical summary data.",
                            "matrices_to_explain": [],
                            "language": "fi",
                            "title_map": {},
                        }
                    ),
                )
            ),
        ),
    ):
        await generate_profile_synthesis_and_pdf_task(
            "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=AsyncMock()
        )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_row_explanation_directive_skips_row_explanations() -> None:
    """Positive: Verify missing row explanation directive skips row explanation synthesis gracefully."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "fi",
        "execution_trace": [],
        "execution_trace_storage_path": None,
        "step_states": {},
        "metadata": {},
    }
    mock_repo.get_workflow_by_id.return_value = _get_base_workflow_dict()
    mock_repo.get_model_registry.return_value = _get_base_model_registry_dict()
    prof_dict = _get_base_profile_dict()
    prof_dict["target_block_order"] = ["matrix_graphs_block", "matrix_summary_table_block"]
    prof_dict["row_explanation_directive"] = None
    mock_repo.get_output_profile_by_id.return_value = prof_dict

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(
                        delta={
                            "distilled_inputs": "Sample analytical summary data.",
                            "matrices_to_explain": [
                                {
                                    "real_matrix_id": "blk_1111222233334444",
                                    "matrix_id": "m0",
                                    "matrix_label": "Target Matrix",
                                    "score": 85.0,
                                    "justification": "Evidence verified.",
                                }
                            ],
                            "language": "fi",
                            "title_map": {},
                        }
                    ),
                )
            ),
        ),
    ):
        await generate_profile_synthesis_and_pdf_task(
            "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=AsyncMock()
        )


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_state_delta_raises_app_exception() -> None:
    """Negative: Verify missing state_delta from distiller hook raises AppException."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "fi",
        "execution_trace": [],
        "execution_trace_storage_path": None,
        "step_states": {},
        "metadata": {},
    }
    mock_repo.get_workflow_by_id.return_value = _get_base_workflow_dict()
    mock_repo.get_output_profile_by_id.return_value = _get_base_profile_dict()

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(return_value=HookResult(success=True, state_delta=None)),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=AsyncMock()
            )
        assert "hook_result.state_delta cannot be None" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_profile_synthesis_missing_distilled_inputs_raises_app_exception() -> None:
    """Negative: Verify missing distilled_inputs from state_delta raises AppException."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "fi",
        "execution_trace": [],
        "execution_trace_storage_path": None,
        "step_states": {},
        "metadata": {},
    }
    mock_repo.get_workflow_by_id.return_value = _get_base_workflow_dict()
    mock_repo.get_output_profile_by_id.return_value = _get_base_profile_dict()

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"other_key": 1}))),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=AsyncMock()
            )
        assert "distilled_inputs missing from state_delta" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_profile_synthesis_no_profile_for_row_explanations_skips_gracefully() -> None:
    """Positive: Verify missing output profile when synthesizing row explanations skips gracefully with a warning."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "output_profile_id": "prof_1111222233334444",
        "status": "RUNNING",
        "target_locale": "fi",
        "execution_trace": [],
        "execution_trace_storage_path": None,
        "step_states": {},
        "metadata": {},
    }
    mock_repo.get_workflow_by_id.return_value = _get_base_workflow_dict()
    mock_repo.get_output_profile_by_id.return_value = None
    mock_repo.get_model_registry.return_value = _get_base_model_registry_dict()

    with (
        patch("backend_v2.worker.get_driver", AsyncMock()),
        patch("backend_v2.worker.UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.worker.synthesis_distiller_hook",
            AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(
                        delta={
                            "distilled_inputs": "Sample analytical summary data.",
                            "matrices_to_explain": [
                                {
                                    "real_matrix_id": "blk_1111222233334444",
                                    "matrix_id": "m0",
                                    "matrix_label": "Target Matrix",
                                    "score": 85.0,
                                    "justification": "Evidence verified.",
                                }
                            ],
                            "language": "fi",
                            "title_map": {},
                        }
                    ),
                )
            ),
        ),
    ):
        await generate_profile_synthesis_and_pdf_task(
            "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444", redis=AsyncMock()
        )





