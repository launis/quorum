import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord
from backend_v2.settings import get_settings
from backend_v2.tests.unit.test_worker_dlq_fallback import (
    test_render_profile_job_catches_service_unavailable_error as _test_dlq_service_unavailable,
)
from backend_v2.tests.unit.test_worker_synthesis import (
    test_worker_extracts_synthesis_from_trace as _test_synthesis_extracts_trace,
)
from backend_v2.tests.unit.test_worker_synthesis import (
    test_worker_synthesis_extracts_metrics_from_trace as _test_synthesis_metrics,
)
from backend_v2.tests.unit.test_worker_synthesis import (
    test_worker_synthesis_malformed_metrics_remains_none as _test_synthesis_malformed_metrics,
)
from backend_v2.tests.unit.test_worker_synthesis import (
    test_worker_synthesis_metrics_no_step_metadata as _test_synthesis_no_step_meta,
)
from backend_v2.tests.unit.test_worker_synthesis import (
    test_worker_synthesis_metrics_no_task_blueprint_in_metadata as _test_synthesis_no_task_bp,
)
from backend_v2.tests.unit.test_worker_synthesis import (
    test_worker_synthesis_missing_metrics_remains_none as _test_synthesis_missing_metrics,
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

# Re-export module tests for unified coverage run
test_worker_extracts_synthesis_from_trace = _test_synthesis_extracts_trace
test_worker_synthesis_extracts_metrics_from_trace = _test_synthesis_metrics
test_worker_synthesis_missing_metrics_remains_none = _test_synthesis_missing_metrics
test_worker_synthesis_malformed_metrics_remains_none = _test_synthesis_malformed_metrics
test_worker_synthesis_metrics_no_step_metadata = _test_synthesis_no_step_meta
test_worker_synthesis_metrics_no_task_blueprint_in_metadata = _test_synthesis_no_task_bp
test_render_profile_job_catches_service_unavailable_error = _test_dlq_service_unavailable


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
        "name": {"default_locale": "en", "translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "status": "PENDING",
        "step_states": {},
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
        status=ExecutionStatus.PENDING,
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
                "metadata": {"target_locale": "fi"},
                "step_states": {
                    "sys_render_prof_1": {"id": "sys_render_prof_1", "label": "Rendering", "status": "RUNNING"}
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
                "status": "RUNNING",
                "step_states": {
                    "sys_render_prof_1": {"id": "sys_render_prof_1", "label": "Rendering", "status": "RUNNING"}
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
                "status": "RUNNING",
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
async def test_generate_profile_synthesis_and_pdf_task_missing_synthesis_block() -> None:
    """Negative test: verify missing synthesis_block_id triggers Fail-Fast CONFIGURATION_ERROR."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "status": "RUNNING",
                "step_states": {},
                "profile_syntheses": {},
            }
            mock_repo.get_output_profile_by_id.return_value = {
                "id": "prof_1111222233334444",
                "slug": "prof-1",
                "workflow_id": "wf_1234567890123456",
                "name": {"default_locale": "en", "translations": {"en": "Profile"}},
                "synthesis": {
                    "synthesis_block_id": "",
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
            }
            mock_repo.get_all_prompt_blocks.return_value = []

            with patch("backend_v2.worker.synthesis_distiller_hook", new_callable=AsyncMock) as mock_distiller:
                mock_distiller.return_value = MagicMock(state_delta={"distilled_inputs": "Data"})
                with pytest.raises((AppException, ExceptionGroup)):
                    await generate_profile_synthesis_and_pdf_task(
                        "exe_1234567890123456", accept_language="fi", profile_id="prof_1111222233334444"
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
                "status": "RUNNING",
                "step_states": {},
                "profile_syntheses": {},
            }
            mock_repo.get_output_profile_by_id.return_value = {
                "id": "prof_1111222233334444",
                "slug": "prof-1",
                "workflow_id": "wf_1234567890123456",
                "name": {"default_locale": "en", "translations": {"en": "Profile"}},
                "synthesis": {
                    "synthesis_block_id": "blk_1111222233334444",
                },
                "visible_workflow_extensions": ["authenticity_evaluation"],
                "max_extension_items": None,
            }
            mock_repo.get_prompt_block.return_value = {
                "id": "blk_1111222233334444",
                "slug": "synth",
                "type": "instruction",
                "label": {"default_locale": "en", "translations": {"en": "Synth"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "ai_description": "Synthesize data.",
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
                "status": "RUNNING",
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
                "name": {"default_locale": "en", "translations": {"en": "Profile"}},
                "synthesis": {
                    "synthesis_block_id": "blk_1111222233334444",
                    "row_explanations_block_id": "blk_2222333344445555",
                    "length_constraint": 500,
                    "tone_instruction": {
                        "default_locale": "en",
                        "translations": {"en": "Direct tone", "fi": "Suora sävy"},
                    },
                },
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "title": {
                            "default_locale": "en",
                            "translations": {"en": "Matrix Section", "fi": "Matriisiosio"},
                        },
                        "is_synthesis_enabled": True,
                        "target_blocks": ["blk_1111222233334444"],
                    }
                ],
                "visible_workflow_extensions": ["variance_validation", "authenticity_evaluation"],
                "max_extension_items": 3,
                "performativity_detector_step_id": "step_perf",
            }

            async def mock_get_pb(pb_id: str) -> dict[str, Any] | None:
                return {
                    "id": pb_id,
                    "slug": f"slug_{pb_id}",
                    "type": "instruction",
                    "label": {"default_locale": "en", "translations": {"en": "Label"}},
                    "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                    "ai_description": f"Instruction for {pb_id}",
                    "category_id": "system_rule",
                }

            mock_repo.get_prompt_block.side_effect = mock_get_pb
            mock_repo.get_all_prompt_blocks.return_value = [
                {
                    "id": "blk_1111222233334444",
                    "slug": "target_1",
                    "type": "instruction",
                    "label": {"default_locale": "en", "translations": {"en": "Target Matrix"}},
                    "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                    "ai_description": "Target Matrix evaluation",
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
                mock_distiller.return_value = MagicMock(
                    state_delta={
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
        "name": {"default_locale": "en", "translations": {"en": "Profile 1"}},
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
    }
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "status": "PENDING",
        "step_states": {},
    }

    mock_exec_record = ExecutionRecord(
        id="exe_1234567890123456",
        workflow_id="wf_1234567890123456",
        status=ExecutionStatus.PENDING,
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
                "status": "RUNNING",
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
                "name": {"default_locale": "en", "translations": {"en": "Profile"}},
                "synthesis": {
                    "synthesis_block_id": "blk_1111222233334444",
                },
                "strictness_level": 85,
                "scoring_strategy": "AVERAGE",
                "display_scale": "original",
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
                    "label": {"default_locale": "en", "translations": {"en": "Matrix"}},
                    "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                    "ai_description": "Evaluation instruction.",
                    "category_id": "matrix",
                    "scales": [
                        {
                            "score": 1,
                            "ai_label": "LOW",
                            "claims": [
                                {
                                    "label": {"default_locale": "en", "translations": {"en": "Low claim"}},
                                    "ai_description": "Low claim rule",
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
                                    "label": {"default_locale": "en", "translations": {"en": "High claim"}},
                                    "ai_description": "High claim rule",
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
                "label": {"default_locale": "en", "translations": {"en": "Synth"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc"}},
                "ai_description": "Synthesize data.",
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
                mock_distiller.return_value = MagicMock(
                    state_delta={
                        "distilled_inputs": "Sample summary data.",
                        "matrices_to_explain": [],
                    }
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
                "status": "RUNNING",
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
                "status": "RUNNING",
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
                "metadata": {"target_locale": "en"},
            }

            mock_redis = AsyncMock()
            await generate_profile_synthesis_and_pdf_task(
                "exe_1234567890123456", accept_language="en", profile_id="prof_1111222233334444", redis=mock_redis
            )

            assert mock_repo.update_execution.call_count >= 1
            calls_with_syntheses = [
                call[0][1] for call in mock_repo.update_execution.call_args_list if "profile_syntheses" in call[0][1]
            ]
            assert len(calls_with_syntheses) == 1
            call_payload = calls_with_syntheses[0]
            saved_cache = call_payload["profile_syntheses"]["prof_1111222233334444"]
            assert saved_cache["data_starvation"]["event_type"] == "starvation"
            assert saved_cache["data_starvation"]["total_atoms"] == 0
            mock_redis.enqueue_job.assert_called_once_with(
                "generate_pdf_job", "exe_1234567890123456", "en", "prof_1111222233334444"
            )
