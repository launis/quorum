from unittest.mock import AsyncMock

import pytest  # force cache reload

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.models.v2_core import ExecutionRecord
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock(spec=AbstractWorkflowRepository)
    repo.get_workflow_by_id.return_value = {
        "id": "wf_test",
        "default_profile_id": "prf_1234abcd",
        "steps": [],
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_1234abcd",
            "slug": "default",
            "workflow_id": "wf_test",
            "name": {"default_locale": "en", "translations": {"fi": "Oletus", "en": "Default"}},
            "layouts": [
                {
                    "preset_view": "1d_metrics",
                    "title": {"default_locale": "en", "translations": {"en": "Metrics"}},
                    "steps": [],
                    "target_blocks": ["*"],
                    "show_text": True,
                }
            ],
        }
    ]
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "metric_category",
            "category_id": "matrix",
            "label": {"default_locale": "en", "translations": {"en": "Metric Category"}},
        }
    ]
    return repo


@pytest.mark.asyncio
async def test_blueprint_zero_math_rounding(mock_repo: AsyncMock) -> None:
    """Epic 13 M3: Enforces float(round(value, 1)) on global_score and matrix axes."""
    transformer = BlueprintTransformer(repo=mock_repo)

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_test",
        status="completed",
        execution_trace=[
            {
                "event_type": "output",
                "step_name": "step_1",
                "content": {
                    "metric_category": 3.14159,  # Should become 3.1
                    "scoring_result": {
                        "total_score": 4.567  # Should become 4.6
                    }
                }
            }
        ]
    )
    mock_repo.get_execution.return_value = mock_execution

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.global_score == 4.6

    assert len(dto.layouts) > 0
    axis = next(a for a in dto.layouts[0].axes if a.name == "Metric Category")
    assert axis.score == 3.1


@pytest.mark.asyncio
async def test_blueprint_synthesis_markdown_packaging(mock_repo: AsyncMock) -> None:
    """Epic 13 M3: Enforces SDUI packaging of synthesized markdown."""
    transformer = BlueprintTransformer(repo=mock_repo)

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_test",
        status="completed",
        execution_trace=[
            {
                "event_type": "output",
                "step_name": "step_1",
                "content": {
                    "synthesized_markdown": "### Title\\n<script>alert('xss');</script>Some content.",
                    "has_warning": True
                }
            }
        ]
    )
    mock_repo.get_execution.return_value = mock_execution

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.has_warning is True

    # Synthesis layout is injected at the beginning (index 0)
    assert len(dto.layouts) >= 1
    synthesis_layout = dto.layouts[0]
    assert synthesis_layout.preset_view == "text_only"

    assert len(synthesis_layout.axes) == 1
    synthesis_axis = synthesis_layout.axes[0]
    assert synthesis_axis.name == "coach-markdown"

    # MVP XSS sanitization test
    assert "<script>" not in synthesis_axis.justification
    assert "Some content" in synthesis_axis.justification
