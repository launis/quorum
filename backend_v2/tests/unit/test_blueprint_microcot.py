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
        "id": "wf_1234567890abcdef",
        "slug": "mock_workflow",
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "status": "published",
        "version": 1,
        "name": {"default_locale": "en", "translations": {"en": "Mock Workflow"}},
        "default_profile_id": "prf_1234567890abcdef",
        "output_profiles": {
            "prf_1234567890abcdef": {
                "name": {"default_locale": "en", "translations": {"en": "Default Profile"}},
                "layouts": [
                    {
                        "preset_view": "2d_compare",
                        "title": {"default_locale": "en", "translations": {"en": "Micro-CoT Map"}},
                        "target_blocks": ["*"],
                        "show_text": True,
                    }
                ],
            }
        },
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_1234567890abcdef",
            "slug": "default",
            "name": {"default_locale": "en", "translations": {"en": "Default Profile"}},
            "workflow_id": "wf_1234567890abcdef",
            "layouts": [
                {
                    "preset_view": "2d_compare",
                    "title": {"default_locale": "en", "translations": {"en": "Micro-CoT Map"}},
                    "target_blocks": ["*"],
                    "show_text": True,
                }
            ],
        }
    ]
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "matrix_kahneman123",
            "slug": "kahneman",
            "category_id": "matrix",
            "label": {"translations": {"en": "Kahneman T1", "fi": "Kaksoisprosessiteoria"}},
            "scales": [
                {"score": 0, "name": {"translations": {"en": "Zero"}}},
                {"score": 3, "name": {"translations": {"en": "Full"}}},
            ],
            "computed_min": 0.0,
            "computed_max": 3.0,
        },
        {
            "id": "matrix_episteeminen123",
            "slug": "episteeminen",
            "category_id": "matrix",
            "label": {"translations": {"en": "Epistemic", "fi": "Episteeminen Nöyryys"}},
            "scales": [
                {"score": 0, "name": {"translations": {"en": "Zero"}}},
                {"score": 5, "name": {"translations": {"en": "Full"}}},
            ],
            "computed_min": 0.0,
            "computed_max": 5.0,
        },
    ]
    return repo


@pytest.mark.asyncio
async def test_blueprint_extracts_nested_microcot_score(mock_repo: Any) -> None:
    """Tier 4 Bug Hunting: Test to reproduce the N/A bug in Flutter charts.
    When the backend Map-Reduce LLM cycle produces a Micro-CoT nested dictionary
    instead of a flat float scalar, BlueprintTransformer currently fails the
    `isinstance(target_val, (int, float))` check because it looks at the entire
    dict rather than extracting the inner `step_4_final_score`.
    """
    mock_repo.get_execution.return_value = ExecutionRecord(
        id="exe_abcdef1234567890",
        workflow_id="wf_1234567890abcdef",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    # Scenario A: Flat scalar (works currently)
                    "matrix_episteeminen123": 1.9,
                    # Scenario B: Nested Micro-CoT dictionary (fails currently and skips setting score)
                    "matrix_kahneman123": {
                        "step_1_evidence": "Found 2 valid arguments",
                        "step_4_final_score": 1.8,
                        "extension_confidence": 0.9,
                    },
                },
            )
        ],
        active_profile_id="prf_1234567890abcdef",
        metadata={"target_locale": "en"},
    )

    transformer = BlueprintTransformer(mock_repo)
    dto = await transformer.build_report_dto("exe_abcdef1234567890", accept_language="en")

    assert isinstance(dto, ReportDataDTO)
    assert len(dto.layouts) > 0
    axes = dto.layouts[0].axes
    assert len(axes) == 2, "Expected 2 axes (Episteeminen and Kahneman)"

    # Map axes by name
    axes_map = {axis.name: axis for axis in axes}

    episteeminen_axis = axes_map.get("Epistemic")
    kahneman_axis = axes_map.get("Kahneman T1")

    assert episteeminen_axis is not None, "Epistemic axis not found"
    assert episteeminen_axis.score == 1.9, "Flat scalar was not extracted correctly"

    assert kahneman_axis is not None, "Kahneman axis not found"

    # This assertion will FAIL (be None) before the bug fix:
    assert kahneman_axis.score == 1.8, (
        f"Expected Micro-CoT score to be 1.8, but got {kahneman_axis.score}. "
        "BlueprintTransformer failed to extract step_4_final_score from nested dict."
    )
