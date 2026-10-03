from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.execution import ExecutionService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.mark.asyncio
async def test_render_execution_json_default_profile_resolves() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    service = ExecutionService(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    exec_id = "exe_00000000000000010000000000000001"
    wf_id = "wf_00000000000000010000000000000001"
    prof_id = "prf_00000000000000010000000000000001"

    record = ExecutionRecord(
        id=exec_id,
        target_locale="en",
        status=ExecutionStatus.PASSED,
        organization_id="org_1",
        metadata=ExecutionMetadata(),
        created_by="u2",
        workflow_id=wf_id,
        profile_syntheses={prof_id: RenderedSynthesisCache()},
    )
    await repo.save_execution(record)

    workflow = Workflow(
        id=wf_id,
        default_profile_id=prof_id,
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="cfg_model_registry_01",
        slug="test",
        version=1,
        name=I18nText(translations={"en": "Test"}),
        description=I18nText(translations={"en": "Test"}),
        status="published",
        steps=[],
    )
    await repo.save_workflow(workflow)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    mock_dto = ReportDataDTO(
        workflow_id=wf_id,
        execution_id=exec_id,
        profile_id=prof_id,
    )

    with patch("backend_v2.services.blueprint.BlueprintTransformer") as mock_transformer_class:
        mock_transformer = AsyncMock()
        mock_transformer.build_report_dto.return_value = mock_dto
        mock_transformer_class.return_value = mock_transformer

        data, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id=exec_id,
            format_type="json",
            profile_id="default",
            accept_language=None,
            arq_pool=arq_pool,
        )

    mock_transformer.build_report_dto.assert_called_once_with(
        exec_id, profile_id=None, accept_language="en", custom_preface_md=None, local_time_str=None
    )

    assert isinstance(data, ReportDataDTO)
    assert data.execution_id == exec_id
    assert data.workflow_id == wf_id
    assert mime == "application/json"
    assert filename is None
