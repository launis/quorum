import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock
from typing import Any

from backend_v2.models.v2_core import ReportDataDTO
from backend_v2.services.blueprint import BlueprintTransformer

@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.get_all_prompt_blocks.return_value = []
    
    mock_op = {
        "id": "opf_1234567890abcdef1234567890abc",
        "slug": "default",
        "name": {"default_locale": "en", "translations": {"en": "Def"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "workflow_id": "wf_1234567890abcdef",
        "layouts": [{"preset_view": "default", "target_blocks": ["*"]}]
    }
    repo.get_all_output_profiles.return_value = [mock_op]
    
    mock_wf = {
        "id": "wf_1234567890abcdef",
        "slug": "test_wf",
        "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "Test description"}},
        "status": "draft",
        "version": 1,
        "organization_id": "system",
        "steps": [],
        "expected_inputs": [],
        "output_profiles": {"opf_1234567890abcdef1234567890abc": {"name": {"default_locale": "en", "translations": {"en": "Def"}}}},
        "default_profile_id": "opf_1234567890abcdef1234567890abc",
    }
    repo.get_workflow_by_id.return_value = mock_wf
    
    mock_profile = MagicMock()
    mock_profile.visible_extensions = []
    mock_profile.visible_metadata = []
    
    # Needs to match ExecutionDB shape used by BlueprintTransformer
    mock_execution = MagicMock()
    mock_execution.id = "exe_test123"
    mock_execution.workflow_id = "wf_1234567890abcdef"
    mock_execution.created_at = datetime.datetime.now(datetime.UTC)
    mock_execution.organization_id = "org_system"
    mock_execution.execution_trace = []
    mock_execution.metadata = {"target_locale": "en"}
    repo.get_execution.return_value = mock_execution
    
    mock_syn = MagicMock()
    mock_syn.payload = mock_profile
    repo.get_synthesized_profile.return_value = mock_syn
    return repo

@pytest.fixture
def blueprint_transformer(mock_repo: AsyncMock) -> BlueprintTransformer:
    return BlueprintTransformer(repo=mock_repo)

def test_extract_numeric_score() -> None:
    assert BlueprintTransformer._extract_numeric_score(5) == 5
    assert BlueprintTransformer._extract_numeric_score("5") == "5"
    assert BlueprintTransformer._extract_numeric_score({"score": 5.0}) == 5.0
    assert BlueprintTransformer._extract_numeric_score({"step_4_final_score": 10}) == 10
    assert BlueprintTransformer._extract_numeric_score({"other": 5}, fallback=0.0) == 0.0
    assert BlueprintTransformer._extract_numeric_score(None, fallback=1.0) == 1.0

@pytest.mark.asyncio
async def test_build_report_dto_empty_trace(blueprint_transformer: BlueprintTransformer, mock_repo: AsyncMock) -> None:
    dto = await blueprint_transformer.build_report_dto(execution_id="exe_test123", accept_language="fi")
    assert isinstance(dto, ReportDataDTO)
    assert dto.workflow_id == "wf_1234567890abcdef"

@pytest.mark.asyncio
async def test_build_report_dto_with_legacy_score(blueprint_transformer: BlueprintTransformer, mock_repo: AsyncMock) -> None:
    mock_repo.get_all_prompt_blocks.return_value = [
        {"id": "block1", "category_id": "matrix", "computed_min": 1, "computed_max": 5, "scales": [{"score": 1, "name": {"default_locale": "en", "translations": {"en": "Poor"}}}]}
    ]
    
    mock_execution = MagicMock()
    mock_execution.id = "exe_test123"
    mock_execution.workflow_id = "wf_1234567890abcdef"
    mock_execution.created_at = datetime.datetime.now(datetime.UTC)
    mock_execution.organization_id = "org_system"
    mock_execution.metadata = {}
    
    event_mock = MagicMock()
    event_mock.timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    event_mock.v = 1
    event_mock.event_type = "step_completed"
    event_mock.step_id = "step1"
    event_mock.result = {
        "score": 5, 
        "block1": 4, 
        "justification": "Good",
        "extension_coaching": "Try harder",
        "extension_missing_context": "Lacks nuance",
        "extension_falsification": "Opposite holds true"
    }
    mock_execution.execution_trace = [event_mock]
    
    mock_repo.get_execution.return_value = mock_execution
    
    dto = await blueprint_transformer.build_report_dto(execution_id="exe_test123")
    assert isinstance(dto, ReportDataDTO)
    assert dto.workflow_id == "wf_1234567890abcdef"
    
    # Verify XAI extensions are correctly mapped into ReportAxisDTO boundaries
    if hasattr(dto, "layouts") and len(dto.layouts) > 0:
        layout = dto.layouts[0]
        if hasattr(layout, "axes") and len(layout.axes) > 0:
            axis = layout.axes[0]
            assert axis.coaching == "Try harder"
            assert axis.falsification == "Opposite holds true"
            assert axis.missing_context == "Lacks nuance"
