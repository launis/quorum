from unittest.mock import AsyncMock, Mock

import pytest

from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
from backend_v2.services.execution import ExecutionService


@pytest.mark.asyncio
async def test_render_execution_json_default_profile_resolves() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.status = ExecutionStatus.PASSED
    mock_record.organization_id = "org_1"
    mock_record.metadata = {}
    mock_record.created_by = "u2"
    mock_record.workflow_id = "wf_1"
    # "prof_1" on oletusprofiili-ID, joten profiilisynteesi löytyy sille
    mock_record.profile_syntheses = {"prof_1": Mock()}
    mock_record.model_copy.return_value = mock_record
    repo_mock.get_execution.return_value = mock_record

    repo_mock.get_workflow_by_id.return_value = {
        "id": "wf_1",
        "default_profile_id": "prof_1",
        "slug": "test",
        "version": 1,
        "name": {},
        "description": {},
        "steps": [],
    }

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    # Mockataan BlueprintTransformer
    mock_dto = Mock()
    mock_dto.evaluative_matrices = []
    mock_dto.informational_matrices = []
    mock_dto.layouts = []
    mock_dto.has_warning = False
    mock_dto.model_dump.return_value = {"execution_id": "exe_1", "workflow_id": "wf_1"}

    with patch("backend_v2.services.execution.BlueprintTransformer") as mock_transformer_class:
        mock_transformer = AsyncMock()
        mock_transformer.build_report_dto.return_value = mock_dto
        mock_transformer_class.return_value = mock_transformer

        with patch(
            "backend_v2.services.execution.Workflow.model_validate", return_value=Mock(default_profile_id="prof_1")
        ):
            data, mime, filename = await service.render_execution(
                initiator=initiator,
                execution_id="exe_1",
                format_type="json",
                profile_id="default",  # <--- Ongelmallinen "default"-arvo
                accept_language=None,
                arq_pool=arq_pool,
            )

    # Varmistetaan, että JSON-formatissa get_report_dto kutsuu arvolla profile_id=None
    mock_transformer.build_report_dto.assert_called_once_with(
        "exe_1", profile_id=None, accept_language=None, custom_preface_md=None, local_time_str=None
    )

    assert data["execution_id"] == "exe_1"
    assert data["workflow_id"] == "wf_1"
    assert mime == "application/json"
    assert filename is None
