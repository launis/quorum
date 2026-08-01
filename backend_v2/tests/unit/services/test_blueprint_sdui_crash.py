import json
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.mark.asyncio
async def test_blueprint_authenticity_evaluation_crash() -> None:
    # Setup mock repositories
    mock_prompt_block_repo = AsyncMock()
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = []

    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "slug": "test",
        "name": "test",
        "description": "test",
        "status": "draft",
        "version": 1,
        "steps": [],
    }
    mock_workflow_repo.get_all_steps.return_value = []

    mock_exec_repo = AsyncMock()
    # Provide a minimal valid ExecutionRecord
    mock_exec_repo.get_execution.return_value = ExecutionRecord(
        id="exec_1234567812345678",
        workflow_id="wf_1234567812345678",
        output_profile_id="prf_1234567812345678",
        status=ExecutionStatus.PASSED,
        context_variables={"step_detector": json.dumps({"raw_score": 75.0})},
        execution_trace=[],
    )

    mock_profile_repo = AsyncMock()
    # Create profile with authenticity_evaluation in extensions but NOT in extension_labels
    mock_profile_dict = {
        "id": "prf_1234567812345678",
        "slug": "test",
        "workflow_id": "wf_1234567812345678",
        "name": {"default_locale": "en", "translations": {"en": "test"}},
        "visible_workflow_extensions": ["authenticity_evaluation"],
        "extension_labels": {},
    }

    mock_profile_repo.get_all_output_profiles.return_value = [mock_profile_dict]

    # Initialize transformer
    transformer = BlueprintTransformer(
        exec_repo=mock_exec_repo,
        output_profile_repo=mock_profile_repo,
        workflow_repo=mock_workflow_repo,
        prompt_block_repo=mock_prompt_block_repo,
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    # Executing build_report_dto should raise AppException due to missing label
    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto("exec_1234567812345678", "prf_1234567812345678", "en")

    assert "Strict Fail-Fast: Missing extension_labels mapping for authenticity_evaluation in OutputProfile." in str(
        exc_info.value.message
    )
