from unittest.mock import AsyncMock

import pytest  # force cache reload

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus, RenderedSynthesisCache
from backend_v2.services.blueprint import BlueprintTransformer


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock(spec=AbstractWorkflowRepository)
    repo.get_workflow_by_id.return_value = {
        "id": "wf_1234abcd1234abcd",
        "slug": "wf_test",
        "name": {"default_locale": "en", "translations": {"en": "Mock"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_1234abcd1234abcd",
        "steps": [],
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_1234abcd1234abcd",
            "slug": "default",
            "workflow_id": "wf_1234abcd1234abcd",
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
            "id": "blk_1234abcd1234abcd",
            "slug": "metric",
            "category_id": "matrix",
            "label": {"default_locale": "en", "translations": {"en": "Metric Category"}},
            "computed_min": 0.0,
            "computed_max": 5.0,
            "scales": [
                {"score": 0, "name": {"translations": {"en": "Zero"}}},
                {"score": 5, "name": {"translations": {"en": "Full"}}},
            ],
        }
    ]
    return repo


@pytest.mark.asyncio
async def test_blueprint_zero_math_rounding(mock_repo: AsyncMock) -> None:
    """Epic 13 M3: Enforces float(round(value, 1)) on global_score and matrix axes."""
    transformer = BlueprintTransformer(repo=mock_repo)

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "blk_1234abcd1234abcd": 3.14159,  # Should become 3.1
                    "scoring_result": {
                        "total_score": 4.567  # Should become 4.6
                    },
                },
            )
        ],
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
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.COMPLETED,
        profile_syntheses={
            "prf_1234abcd1234abcd": RenderedSynthesisCache(
                synthesized_markdown="### Title\\n<script>alert('xss');</script>Some content."
            )
        },
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "has_warning": True,
                },
            )
        ],
    )
    mock_repo.get_execution.return_value = mock_execution

    dto = await transformer.build_report_dto("exe_1111111122222222")
    assert dto.has_warning is True

    # MVP XSS sanitization test
    assert dto.synthesized_markdown is not None
    assert "<script>" not in dto.synthesized_markdown
    assert "Some content." in dto.synthesized_markdown
