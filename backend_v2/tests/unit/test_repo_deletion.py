import pytest
from unittest.mock import AsyncMock
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes

@pytest.fixture
def mock_driver():
    driver = AsyncMock()
    return driver

@pytest.mark.asyncio
async def test_delete_matrix_blocks_orphan_data(mock_driver):
    repo = UnifiedWorkflowRepository(driver=mock_driver)
    
    # Mock get_matrix_by_id to simulate the matrix exists
    repo.get_matrix_by_id = AsyncMock(return_value={"id": "m1"})
    
    # Mock get_all_task_blueprints to return a blueprint using 'm1'
    repo.get_all_task_blueprints = AsyncMock(return_value=[
        {"id": "bp1", "prompt_blocks": ["m1", "m2"]}
    ])
    
    # Should raise AppException with RESOURCE_IN_USE
    with pytest.raises(AppException) as exc_info:
        await repo.delete_matrix("m1")
        
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE
    assert "Tuhoaminen estetty: PromptBlock 'm1' on sidottu Blueprinttiin 'bp1'." in exc_info.value.message
    
    # Should bypass if force_delete=True
    await repo.delete_matrix("m1", force_delete=True)
    mock_driver.delete.assert_called_with("matrices", "m1")
