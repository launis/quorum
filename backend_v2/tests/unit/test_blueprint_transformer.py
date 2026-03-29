from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ReportDataDTO
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    repo.get_workflow_by_id.return_value = {
        "name": {"default_locale": "en", "translations": {"en": "Mock Workflow", "fi": "Testi Työnkulku"}},
        "default_profile_id": "prf_default1",
        "output_profiles": {
            "prf_default1": {
                "name": {"default_locale": "en", "translations": {"en": "Default"}},
                "workflow_id": "wf_1",
                "layouts": [
                    {
                        "layout_type": "box_1d",
                        "title": {"default_locale": "en", "translations": {"en": "Title"}},
                        "components": ["*"],
                        "show_text": True,
                    }
                ],
            }
        },
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_default1",
            "slug": "prf_default1",
            "name": {"default_locale": "en", "translations": {"en": "Default"}},
            "workflow_id": "wf_1",
            "layouts": [
                {
                    "layout_type": "box_1d",
                    "title": {"default_locale": "en", "translations": {"en": "Title"}},
                    "components": ["*"],
                    "show_text": True,
                }
            ],
        }
    ]
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "matrix_logic1234",
            "slug": "matrix_logic1234",
            "category_id": "matrix",
            "label": {"translations": {"fi": "Logiikka", "en": "Logic"}},
            "scales": [
                {"score": 0, "name": {"translations": {"fi": "Nolla", "en": "Zero"}}},
                {"score": 100, "name": {"translations": {"fi": "Täysi", "en": "Full"}}},
            ],
        }
    ]
    return repo


@pytest.mark.asyncio
async def test_build_report_dto_maps_correctly(mock_repo: Any) -> None:
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_0000test001",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    "matrix_logic1234": 75.0,
                    "matrix_logic1234_justification": "Very logical",
                    "synthesis": "Great job",
                },
            )
        ],
        active_profile_id="prf_default1",
        metadata={"target_locale": "en"},
    )
    transformer = BlueprintTransformer(mock_repo)
    dto = await transformer.build_report_dto("testexec_0000test001", accept_language="en")

    assert isinstance(dto, ReportDataDTO)
    print("DEBUG: layout components from profile:", mock_repo.get_all_output_profiles.return_value)
    projector = __import__("backend_v2.models.state", fromlist=["StateProjector"]).StateProjector()
    res = projector.fold_trace(mock_repo.get_execution.return_value.execution_trace)
    print("DEBUG: folded results:", res)
    print("DEBUG: layouts array lengths:", len(dto.layouts))
    assert len(dto.layouts) == 1
    assert len(dto.layouts[0].axes) == 1

    axis = dto.layouts[0].axes[0]
    assert axis.name in ["Mock Workflow", "step_analyst", "matrix_logic1234", "test_k", "Logic"]
    assert axis.score == 75.0
    assert axis.justification == "Very logical"


@pytest.mark.asyncio
async def test_graceful_degradation_missing_fields(mock_repo: Any) -> None:
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="testexec_0000test002",
        workflow_id="wf_1",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[],
        active_profile_id="prf_default1",
        metadata={"target_locale": "fi"},
    )
    transformer = BlueprintTransformer(mock_repo)
    dto = await transformer.build_report_dto("testexec_0000test002")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) == 0
