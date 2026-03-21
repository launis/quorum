from unittest.mock import AsyncMock

import pytest

from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import ExecutionRecord, ReportDataDTO
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_workflow_by_id.return_value = {
        "name": {
            "default_locale": "en",
            "translations": {"en": "Mock Workflow", "fi": "Testi Työnkulku"}
        },
        "output_profiles": {
            "default": {
                "name": {"en": "Default"},
                "layouts": [{"preset_view": "1d_metrics", "steps": [], "show_text": True}]
            }
        }
    }
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "matrix_logic1234",
            "slug": "matrix_logic1234",
            "label": {"translations": {"fi": "Logiikka", "en": "Logic"}},
            "scales": [
                {"score": 0, "name": {"translations": {"fi": "Nolla", "en": "Zero"}}},
                {"score": 100, "name": {"translations": {"fi": "Täysi", "en": "Full"}}}
            ]
        }
    ]
    return repo

@pytest.mark.asyncio
async def test_build_report_dto_maps_correctly(mock_repo):
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_0000test001",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        results={
            "step_analyst": {
                "score": 75.0,
                "justification": "Very logical",
                "synthesis": "Great job"
            }
        },
        active_profile_id="default",
        metadata={"target_locale": "en"}
    )
    transformer = BlueprintTransformer(mock_repo)
    dto = await transformer.build_report_dto("testexec_0000test001", accept_language="en")

    assert isinstance(dto, ReportDataDTO)
    assert dto.synthesis == "Great job"
    assert len(dto.layouts) == 1
    assert len(dto.layouts[0].axes) == 1

    axis = dto.layouts[0].axes[0]
    assert axis.name in ["Mock Workflow", "step_analyst", "score", "test_k"]
    assert axis.score == 75.0
    assert axis.justification == "Very logical"

@pytest.mark.asyncio
async def test_graceful_degradation_missing_fields(mock_repo):
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_0000test002",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        results={},
        active_profile_id="default",
        metadata={"target_locale": "fi"}
    )
    transformer = BlueprintTransformer(mock_repo)
    dto = await transformer.build_report_dto("testexec_0000test002")

    assert isinstance(dto, ReportDataDTO)
    assert dto.synthesis is None
    assert len(dto.layouts) == 0
