import json
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    ExtensionMetricsDTO,
    RenderedSynthesisCache,
)
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.mark.asyncio
async def test_blueprint_authenticity_evaluation_success() -> None:
    # Setup mock repositories
    mock_prompt_block_repo = AsyncMock()
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = []

    mock_workflow_repo = AsyncMock()
    mock_wf = AsyncMock()
    mock_wf.default_scoring_strategy = "AVERAGE"
    mock_wf.default_strictness_level = 85
    mock_workflow_repo.get_workflow.return_value = mock_wf
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
        active_profile_id="prf_1234567812345678",
        status=ExecutionStatus.PASSED,
        context_variables={"step_detector": json.dumps({"raw_score": 75.0})},
        execution_trace=[],
        profile_syntheses={
            "prf_1234567812345678": RenderedSynthesisCache(
                extension_metrics=ExtensionMetricsDTO(authenticity_score=75.0)
            )
        },
    )

    mock_profile_repo = AsyncMock()
    mock_profile_dict = {
        "id": "prf_1234567812345678",
        "slug": "test",
        "workflow_id": "wf_1234567812345678",
        "name": {"translations": {"en": "test"}},
        "target_block_order": ["authenticity_evaluation_block"],
        "visible_workflow_extensions": ["authenticity_evaluation"],
    }

    mock_profile_repo.get_all_output_profiles.return_value = [mock_profile_dict]
    mock_profile_repo.get_output_profile.return_value = mock_profile_dict
    mock_profile_repo.get_profile_synthesis_cache.return_value = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(authenticity_score=75.0)
    )

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

    report = await transformer.build_report_dto("exec_1234567812345678", "prf_1234567812345678", "en")
    assert report is not None
    assert len(report.inner_sdui_blocks) >= 1
