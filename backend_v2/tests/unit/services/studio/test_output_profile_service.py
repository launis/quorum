"""Tests for StudioOutputProfileService."""
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData
from backend_v2.models.v2_core import OutputProfile, OutputLayoutBlock
from backend_v2.models.enums import TargetBlockType
from backend_v2.services.studio.output_profile_service import StudioOutputProfileService


@pytest.fixture
def mock_output_profile_repo():
    return AsyncMock()


@pytest.fixture
def mock_workflow_service():
    return AsyncMock()


@pytest.fixture
def service(mock_output_profile_repo, mock_workflow_service):
    return StudioOutputProfileService(
        output_profile_repo=mock_output_profile_repo,
        workflow_service=mock_workflow_service,
    )


@pytest.mark.asyncio
async def test_save_output_profile_allows_target_block_types(service, mock_workflow_service):
    """Test that virtual blocks from TargetBlockType are allowed without failing validation."""
    initiator = TokenData(id="test_user", role="ADMIN", organization_id="root")
    
    # Mock Workflow
    workflow = AsyncMock()
    workflow.slug = "test_wf"
    workflow.steps = []
    from unittest.mock import Mock
    workflow.get_allowed_layout_targets = Mock(return_value={TargetBlockType.GLOBAL_SCORE_BLOCK.value})
    
    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []
    
    # Mock return from repo
    service.output_profile_repo.get_output_profile_by_id.return_value = {
        "id": "opt_1234567890abcdef",
        "slug": "opt_123",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "organization_id": "root",
        "layouts": []
    }
    
    # Create an OutputProfile that includes "global_score_block"
    profile = OutputProfile(
        id="opt_1234567890abcdef",
        slug="opt_123",
        workflow_id="wf_123",
        name={"default_locale": "en", "translations": {"en": "Test"}},
        organization_id="root",
        layouts=[
            OutputLayoutBlock(
                preset_view="text_only",
                target_blocks=[TargetBlockType.GLOBAL_SCORE_BLOCK.value]
            )
        ]
    )
    
    # This should NOT raise AppException
    await service.save_output_profile(initiator, profile.id, profile)
    
    # If it raised AppException, the test would fail. We also verify it called create
    assert service.output_profile_repo.create_output_profile.called
