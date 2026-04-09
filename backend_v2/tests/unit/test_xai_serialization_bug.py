import pytest
from unittest.mock import AsyncMock
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus, RenderedSynthesisCache
from backend_v2.services.blueprint import BlueprintTransformer

@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock(spec=AbstractWorkflowRepository)
    repo.get_workflow_by_id.return_value = {
        "id": "wf_test",
        "default_profile_id": "prf_1234abcd1234abcd",
        "steps": [],
    }
    repo.get_all_output_profiles.return_value = [
        {
            "id": "prf_1234abcd1234abcd",
            "slug": "default",
            "workflow_id": "wf_test",
            "name": {"default_locale": "en", "translations": {"fi": "Oletus", "en": "Default"}},
            "layouts": [
                {
                    "preset_view": "3d_complex",
                    "title": {"default_locale": "en", "translations": {"en": "Metrics"}},
                    "steps": [],
                    "target_blocks": ["*"],
                    "text_delivery_mode": "full",
                }
            ],
            "visible_extensions": ["remediation_steps"]
        }
    ]
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "metric_category_1",
            "category_id": "matrix",
            "label": {"default_locale": "en", "translations": {"en": "Metric Category 1"}},
        },
        {
            "id": "metric_category_2",
            "category_id": "matrix",
            "label": {"default_locale": "en", "translations": {"en": "Metric Category 2"}},
        },
        {
            "id": "metric_category_3",
            "category_id": "matrix",
            "label": {"default_locale": "en", "translations": {"en": "Metric Category 3"}},
        }
    ]
    return repo

@pytest.mark.asyncio
async def test_xai_remediation_serialization_bug(mock_repo: AsyncMock) -> None:
    """Test that XAI extension items like remediation_steps are properly JSON serialized."""
    transformer = BlueprintTransformer(repo=mock_repo)

    mock_execution = ExecutionRecord(
        id="exe_1111111122222222",
        workflow_id="wf_test",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "metric_category_1": {
                        "step_4_final_score": 3.14159,
                        "extension_remediation_steps": ["Step 1: Do this", "Step 2: Do that"],
                    },
                    "metric_category_2": 2.0,
                    "metric_category_3": 1.0,
                },
            )
        ],
    )
    mock_repo.get_execution.return_value = mock_execution

    dto = await transformer.build_report_dto("exe_1111111122222222")
    
    # Assert remediation_steps was grouped properly
    assert "remediation_steps" in dto.grouped_extensions
    items = dto.grouped_extensions["remediation_steps"]
    assert len(items) > 0
    
    first_item = items[0]
    
    # Check that it's a dict and ready for FastAPI, not a naked object or string!
    assert isinstance(first_item, dict), "Highlight item MUST be a dict to prevent string literal serialization"
    
    # Check that array values were properly parsed as newlines, not stringified python arrays
    assert "content" in first_item
    content = first_item["content"]
    assert "['" not in content, "Array should not be stringified literally as ['Step 1', ...]"
    assert "Step 1: Do this" in content
    assert "Step 2: Do that" in content
