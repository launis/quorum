"""Unit tests for ExecutionService facade (Strangler Fig pattern)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.execution import ExecutionCreate, ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputsIngress
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest
from backend_v2.models.dtos.render import RenderExecutionResultDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.view.sdui import ReportView
from backend_v2.services.execution.facade import ExecutionService, create_execution_record


@pytest.fixture
def initiator() -> TokenData:
    """Fixture providing standard user token data."""
    return TokenData(id="usr_123", role=UserRole.MEMBER, organization_id="org_123")


@pytest.fixture
def mock_execution_service() -> tuple[ExecutionService, dict[str, MagicMock]]:
    """Fixture providing ExecutionService facade with mocked sub-services."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()

    service = ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
    )

    subservices = {
        "lifecycle": MagicMock(),
        "ingress": MagicMock(),
        "resumption": MagicMock(),
        "override": MagicMock(),
        "stream": MagicMock(),
        "context": MagicMock(),
        "renderer": MagicMock(),
    }

    service._lifecycle = subservices["lifecycle"]
    service._ingress = subservices["ingress"]
    service._resumption = subservices["resumption"]
    service._override = subservices["override"]
    service._stream = subservices["stream"]
    service._context = subservices["context"]
    service._renderer = subservices["renderer"]

    return service, subservices


def test_execution_service_init_with_defaults() -> None:
    """Verify ExecutionService initializes correctly with default optional dependencies."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    service = ExecutionService(exec_repo=exec_repo, workflow_repo=workflow_repo)
    assert service.exec_repo is exec_repo
    assert service.workflow_repo is workflow_repo
    assert service.comp_repo is None
    assert service.export_service is not None
    assert service.storage is not None
    assert callable(create_execution_record)


def test_execution_service_init_with_custom_deps() -> None:
    """Verify ExecutionService initializes correctly with custom injected dependencies."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    custom_export = MagicMock()
    custom_storage = MagicMock()
    custom_usage = MagicMock()
    custom_executor = MagicMock()

    service = ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        usage_service=custom_usage,
        executor=custom_executor,
        export_service=custom_export,
        storage_driver=custom_storage,
    )
    assert service.export_service is custom_export
    assert service.storage is custom_storage
    assert service.usage_service is custom_usage
    assert service.executor is custom_executor


@pytest.mark.asyncio
async def test_list_executions(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify list_executions delegates to _lifecycle.list_executions."""
    service, subs = mock_execution_service
    expected = [MagicMock(spec=ExecutionRecord)]
    subs["lifecycle"].list_executions = AsyncMock(return_value=expected)

    result = await service.list_executions(initiator)
    assert result == expected
    subs["lifecycle"].list_executions.assert_awaited_once_with(initiator)


@pytest.mark.asyncio
async def test_get_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify get_execution delegates to _lifecycle.get_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ExecutionRecord)
    subs["lifecycle"].get_execution = AsyncMock(return_value=expected)

    result = await service.get_execution(initiator, "exe_123", hydrate=True, skip_resumability=False)
    assert result == expected
    subs["lifecycle"].get_execution.assert_awaited_once_with(initiator, "exe_123", True, False)


@pytest.mark.asyncio
async def test_delete_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify delete_execution delegates to _lifecycle.delete_execution."""
    service, subs = mock_execution_service
    subs["lifecycle"].delete_execution = AsyncMock(return_value=True)

    result = await service.delete_execution(initiator, "exe_123")
    assert result is True
    subs["lifecycle"].delete_execution.assert_awaited_once_with(initiator, "exe_123")


@pytest.mark.asyncio
async def test_start_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify start_execution delegates to _ingress.start_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ExecutionRecord)
    subs["ingress"].start_execution = AsyncMock(return_value=expected)

    payload = ExecutionCreate(
        workflow_id="wf_123",
        target_locale="fi",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"key": "val"}),
    )
    arq_pool = AsyncMock()

    result = await service.start_execution(initiator, payload, arq_pool)
    assert result == expected
    subs["ingress"].start_execution.assert_awaited_once_with(initiator, payload, arq_pool, None)


@pytest.mark.asyncio
async def test_get_workflow_ui_schema(mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]]) -> None:
    """Verify get_workflow_ui_schema delegates to _ingress.get_workflow_ui_schema."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=WorkflowSchemaResponseDTO)
    subs["ingress"].get_workflow_ui_schema = AsyncMock(return_value=expected)

    result = await service.get_workflow_ui_schema("wf_123")
    assert result == expected
    subs["ingress"].get_workflow_ui_schema.assert_awaited_once_with("wf_123")


@pytest.mark.asyncio
async def test_check_resumability(mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]]) -> None:
    """Verify check_resumability delegates to _resumption.check_resumability."""
    service, subs = mock_execution_service
    subs["resumption"].check_resumability = AsyncMock(return_value=True)

    record = MagicMock(spec=ExecutionRecord)
    result = await service.check_resumability(record)
    assert result is True
    subs["resumption"].check_resumability.assert_awaited_once_with(record)


@pytest.mark.asyncio
async def test_resume_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify resume_execution delegates to _resumption.resume_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ExecutionRecord)
    subs["resumption"].resume_execution = AsyncMock(return_value=expected)

    arq_pool = AsyncMock()
    result = await service.resume_execution(initiator, "exe_123", arq_pool)
    assert result == expected
    subs["resumption"].resume_execution.assert_awaited_once_with(initiator, "exe_123", arq_pool)


@pytest.mark.asyncio
async def test_override_atom(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify override_atom delegates to _override.override_atom."""
    service, subs = mock_execution_service
    subs["override"].override_atom = AsyncMock()

    payload = HumanOverrideRequest(new_status=ExecutionStatus.PASSED, reason="Human override test")
    await service.override_atom(initiator, "exe_123", "atm_123", payload)
    subs["override"].override_atom.assert_awaited_once_with(initiator, "exe_123", "atm_123", payload)


@pytest.mark.asyncio
async def test_reject_evidence_quote(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify reject_evidence_quote delegates to _override.reject_evidence_quote."""
    service, subs = mock_execution_service
    subs["override"].reject_evidence_quote = AsyncMock()

    await service.reject_evidence_quote(initiator, "exe_123", "evq_123", "Hallucination")
    subs["override"].reject_evidence_quote.assert_awaited_once_with(initiator, "exe_123", "evq_123", "Hallucination")


@pytest.mark.asyncio
async def test_clear_profile_synthesis(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify clear_profile_synthesis delegates to _override.clear_profile_synthesis."""
    service, subs = mock_execution_service
    subs["override"].clear_profile_synthesis = AsyncMock()

    await service.clear_profile_synthesis(initiator, "exe_123", "prf_123")
    subs["override"].clear_profile_synthesis.assert_awaited_once_with(initiator, "exe_123", "prf_123")


@pytest.mark.asyncio
async def test_stream_status(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify stream_status delegates to _stream.stream_status."""
    service, subs = mock_execution_service

    async def sample_stream(init: TokenData, eid: str):
        yield "event: progress\ndata: {}\n\n"
        yield "event: done\ndata: {}\n\n"

    subs["stream"].stream_status = sample_stream

    chunks = [chunk async for chunk in service.stream_status(initiator, "exe_123")]
    assert len(chunks) == 2
    assert "progress" in chunks[0]
    assert "done" in chunks[1]


@pytest.mark.asyncio
async def test_get_frozen_context_bytes(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify get_frozen_context_bytes delegates to _context.get_frozen_context_bytes."""
    service, subs = mock_execution_service
    expected = (b'{"test": 1}', "frozen_context.json")
    subs["context"].get_frozen_context_bytes = AsyncMock(return_value=expected)

    result = await service.get_frozen_context_bytes(initiator, "exe_123")
    assert result == expected
    subs["context"].get_frozen_context_bytes.assert_awaited_once_with(initiator, "exe_123")


@pytest.mark.asyncio
async def test_get_execution_export_bytes(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify get_execution_export_bytes delegates to _renderer.get_execution_export_bytes."""
    service, subs = mock_execution_service
    expected = (b"excel_bytes", "report.xlsx")
    subs["renderer"].get_execution_export_bytes = AsyncMock(return_value=expected)

    result = await service.get_execution_export_bytes(initiator, "exe_123")
    assert result == expected
    subs["renderer"].get_execution_export_bytes.assert_awaited_once_with(initiator, "exe_123")


@pytest.mark.asyncio
async def test_render_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify render_execution delegates to _renderer.render_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=RenderExecutionResultDTO)
    subs["renderer"].render_execution = AsyncMock(return_value=expected)

    arq_pool = AsyncMock()
    result = await service.render_execution(
        initiator=initiator,
        execution_id="exe_123",
        format_type="sdui",
        profile_id="prf_123",
        accept_language="fi",
        arq_pool=arq_pool,
        custom_preface_md="# Preface",
        local_time_str="2026-09-21 12:00",
    )
    assert result == expected
    subs["renderer"].render_execution.assert_awaited_once_with(
        initiator, "exe_123", "sdui", "prf_123", "fi", arq_pool, "# Preface", "2026-09-21 12:00"
    )


@pytest.mark.asyncio
async def test_get_report_dto(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify get_report_dto delegates to _renderer.get_report_dto."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ReportDataDTO)
    subs["renderer"].get_report_dto = AsyncMock(return_value=expected)

    result = await service.get_report_dto(initiator, "exe_123")
    assert result == expected
    subs["renderer"].get_report_dto.assert_awaited_once_with(initiator, "exe_123")


@pytest.mark.asyncio
async def test_get_sdui_view(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify get_sdui_view delegates to _renderer.get_sdui_view."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ReportView)
    subs["renderer"].get_sdui_view = AsyncMock(return_value=expected)

    result = await service.get_sdui_view(initiator, "exe_123")
    assert result == expected
    subs["renderer"].get_sdui_view.assert_awaited_once_with(initiator, "exe_123")


@pytest.mark.asyncio
async def test_enqueue_pdf_generation(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify enqueue_pdf_generation delegates to _renderer.enqueue_pdf_generation."""
    service, subs = mock_execution_service
    subs["renderer"].enqueue_pdf_generation = AsyncMock()

    arq_pool = AsyncMock()
    await service.enqueue_pdf_generation(
        initiator=initiator,
        execution_id="exe_123",
        accept_language="en",
        profile_id="prf_123",
        arq_pool=arq_pool,
        custom_preface_md="# Preface",
        local_time_str="2026-09-21 12:00",
    )
    subs["renderer"].enqueue_pdf_generation.assert_awaited_once_with(
        initiator, "exe_123", "en", "prf_123", arq_pool, "# Preface", "2026-09-21 12:00"
    )
