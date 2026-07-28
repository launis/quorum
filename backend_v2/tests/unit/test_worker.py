from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import WorkflowNotFoundError
from backend_v2.worker import execute_workflow_job, health_check, startup


@pytest.mark.asyncio
async def test_health_check() -> None:
    res = await health_check({})
    assert res == "OK"


@pytest.mark.asyncio
async def test_startup() -> None:
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
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = None

    mock_engine = AsyncMock()

    ctx: dict[str, Any] = {"repository": mock_repo, "engine": mock_engine}

    with pytest.raises(WorkflowNotFoundError):
        await execute_workflow_job(ctx, "nonexistent", {})


@pytest.mark.asyncio
async def test_execute_workflow_job_success() -> None:
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "default_strictness_level": 50,
        "default_scoring_strategy": "AVERAGE",
    }
    mock_repo.get_output_profile_by_id.return_value = None
    mock_repo.get_execution.return_value = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890123456",
        "status": "PENDING",
        "step_states": {},
    }
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.v2_core import ExecutionRecord

    mock_exec_record = ExecutionRecord(
        id="exe_1234567890123456", workflow_id="wf_1234567890123456", status=ExecutionStatus.PENDING, step_states={}
    )
    mock_engine = AsyncMock()
    mock_engine.execute_workflow.return_value = mock_exec_record

    ctx: dict[str, Any] = {"repository": mock_repo, "engine": mock_engine, "redis": AsyncMock()}

    inputs: dict[str, Any] = {}
    res = await execute_workflow_job(
        ctx,
        workflow_id="wf_1234567890123456",
        inputs=inputs,
        execution_id="exe_1234567890123456",
        organization_id="org_1",
        user_id="usr_1",
    )

    assert res["status"] == "COMPLETED"
    assert res["execution_id"] == "exe_1234567890123456"
    assert inputs["organization_id"] == "org_1"
    assert inputs["user_id"] == "usr_1"
    mock_engine.execute_workflow.assert_called_once()
    mock_repo.update_execution.assert_called_once()
    ctx["redis"].enqueue_job.assert_called_once_with("render_profile_job", "exe_1234567890123456", profile_id="prof_1")


@pytest.mark.asyncio
async def test_generate_pdf_job() -> None:
    from backend_v2.worker import generate_pdf_job

    with patch("backend_v2.worker.generate_pdf_task") as mock_task:
        res = await generate_pdf_job({}, "exe_1234567890123456", "en-US", "prof_1")
        assert res == "PDF Generated for exe_1234567890123456"
        mock_task.assert_called_once_with("exe_1234567890123456", "en-US", "prof_1")


@pytest.mark.asyncio
async def test_render_profile_job() -> None:
    from backend_v2.worker import render_profile_job

    with patch("backend_v2.worker.generate_profile_synthesis_and_pdf_task") as mock_task:
        ctx = {"redis": AsyncMock()}
        res = await render_profile_job(ctx, "exe_1234567890123456", "en-US", "prof_1")
        assert res == "Render Job Completed for exe_1234567890123456"
        mock_task.assert_called_once_with("exe_1234567890123456", "en-US", "prof_1", ctx["redis"])


@pytest.mark.asyncio
async def test_generate_pdf_task_execution_not_found() -> None:
    from backend_v2.worker import generate_pdf_task

    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_execution.return_value = None

            await generate_pdf_task("exe_1234567890123456")
            mock_repo.get_execution.assert_called_once_with("exe_1234567890123456")


@pytest.mark.asyncio
async def test_generate_profile_synthesis_and_pdf_task_not_found() -> None:
    from backend_v2.worker import generate_profile_synthesis_and_pdf_task

    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_execution.return_value = None

            await generate_profile_synthesis_and_pdf_task("exe_1234567890123456")
            mock_repo.get_execution.assert_called_once_with("exe_1234567890123456")


@pytest.mark.asyncio
async def test_generate_pdf_task_slop_penalty_ignores_metadata() -> None:
    from unittest.mock import MagicMock

    from backend_v2.worker import generate_pdf_task

    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "status": "PENDING",
                "step_states": {},
            }

            with patch("backend_v2.worker.BlueprintTransformer") as mock_transformer_class:
                mock_transformer = AsyncMock()
                mock_transformer_class.return_value = mock_transformer

                mock_dto = MagicMock()
                mock_layout = MagicMock()
                mock_layout.metadata = None
                mock_layout.synthesis_blocks = [{"text": "this is bad PENALTY_SLOP: too generic"}]
                mock_dto.layouts = [mock_layout]
                mock_transformer.build_report_dto.return_value = mock_dto

                with patch("backend_v2.worker.PdfReportService") as mock_pdf_class:
                    mock_pdf = AsyncMock()
                    mock_pdf_class.return_value = mock_pdf
                    mock_pdf.generate_execution_pdf.return_value = b"pdf"

                    with patch("backend_v2.worker.get_storage_driver") as mock_storage_class:
                        mock_storage = AsyncMock()
                        mock_storage_class.return_value = mock_storage
                        mock_storage.save.return_value = "saved.pdf"

                        await generate_pdf_task("exe_1234567890123456")
                        assert mock_repo.update_execution.call_count >= 1
                        mock_pdf.generate_execution_pdf.assert_called_once()
                        mock_storage.save.assert_called_once()


@pytest.mark.asyncio
async def test_generate_pdf_task_slop_penalty_ignores_missing_penalty_type() -> None:
    from unittest.mock import MagicMock

    from backend_v2.worker import generate_pdf_task

    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "status": "PENDING",
                "step_states": {},
            }

            with patch("backend_v2.worker.BlueprintTransformer") as mock_transformer_class:
                mock_transformer = AsyncMock()
                mock_transformer_class.return_value = mock_transformer

                mock_dto = MagicMock()
                mock_layout = MagicMock()
                # Metadata exists but is missing penalty_type
                mock_layout.metadata = {"some_other_key": "value"}
                mock_layout.synthesis_blocks = [{"text": "this is bad PENALTY_SLOP: too generic"}]
                mock_dto.layouts = [mock_layout]
                mock_transformer.build_report_dto.return_value = mock_dto

                with patch("backend_v2.worker.PdfReportService") as mock_pdf_class:
                    mock_pdf = AsyncMock()
                    mock_pdf_class.return_value = mock_pdf
                    mock_pdf.generate_execution_pdf.return_value = b"pdf"

                    with patch("backend_v2.worker.get_storage_driver") as mock_storage_class:
                        mock_storage = AsyncMock()
                        mock_storage_class.return_value = mock_storage
                        mock_storage.save.return_value = "saved.pdf"

                        await generate_pdf_task("exe_1234567890123456")
                        assert mock_repo.update_execution.call_count >= 1
                        mock_pdf.generate_execution_pdf.assert_called_once()
                        mock_storage.save.assert_called_once()
