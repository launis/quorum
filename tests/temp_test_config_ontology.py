import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from backend.api.routes.config.ontology import (
    get_known_dimensions,
    delete_dimension,
    update_dimension
)
from backend.models.dtos.config import DimensionDefinition, DimensionDeleteResponse
from backend.exceptions import AppException, ResourceNotFoundError, ErrorCodes, ConflictError

class TestConfigOntologyRouter:
    
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        table = MagicMock()
        db.table.return_value = table
        return db

    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock()
        return repo

    def test_get_known_dimensions_success(self, mock_db):
        """Test getting dimensions successfully."""
        # Setup
        mock_data = [
            {"id": "dim2", "label": "Dimension 2"},
            {"id": "dim1", "label": "Dimension 1"}
        ]
        mock_db.table().all.return_value = mock_data

        # Execute
        result = get_known_dimensions(db=mock_db)

        # Verify
        assert len(result) == 2
        assert result[0].id == "dim1" # Sorted by ID
        assert result[1].id == "dim2"
        print("\n[TEST] Get Known Dimensions: Success Sorted")

    async def test_delete_dimension_success(self, mock_db, mock_repo):
        """Test deleting an unused dimension."""
        # Setup
        dim_id = "unused_dim"
        mock_db.table().contains.return_value = True # Exists
        mock_repo.get_components_using_dimension.return_value = [] # Not used

        # Execute
        result = await delete_dimension(dim_id, db=mock_db, repo=mock_repo)

        # Verify
        assert isinstance(result, DimensionDeleteResponse)
        assert result.id == dim_id
        assert result.status == "deleted"
        mock_db.table().remove.assert_called_once()
        print("\n[TEST] Delete Dimension: Success")

    async def test_delete_dimension_conflict(self, mock_db, mock_repo):
        """Test deleting a used dimension throws ConflictError."""
        # Setup
        dim_id = "used_dim"
        mock_db.table().contains.return_value = True # Exists
        mock_repo.get_components_using_dimension.return_value = ["matrix_1"] # Used
        
        # Mock component search for name
        mock_db.table().search.return_value = [{"name": "Test Matrix"}]

        # Execute & Verify
        try:
            await delete_dimension(dim_id, db=mock_db, repo=mock_repo)
            assert False, "Should have raised ConflictError"
        except ConflictError as e:
            assert e.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE
            assert e.status_code == status.HTTP_409_CONFLICT
            assert "matrix" in e.message.lower()
            print("\n[TEST] Delete Dimension: Caught ConflictError (Blocked by Usage)")

    async def test_update_dimension_id_mismatch(self, mock_db, mock_repo):
        """Test update fails fast on ID mismatch."""
        # Setup
        dim_id = "dim_1"
        payload = DimensionDefinition(id="dim_2", label="Mismatch")

        # Execute & Verify
        try:
            await update_dimension(dim_id, payload, db=mock_db, repo=mock_repo)
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.DIMENSION_ID_MISMATCH
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            print("\n[TEST] Update Dimension: Caught ID Mismatch")

    async def test_update_dimension_success(self, mock_db, mock_repo):
        """Test updating a dimension successfully."""
        # Setup
        dim_id = "dim_1"
        payload = DimensionDefinition(id="dim_1", label="Updated")
        mock_db.table().contains.return_value = True

        # Execute
        result = await update_dimension(dim_id, payload, db=mock_db, repo=mock_repo)

        # Verify
        assert result.label == "Updated"
        mock_db.table().update.assert_called_once()
        print("\n[TEST] Update Dimension: Success")

if __name__ == "__main__":
    import asyncio
    # Manual run for quick verification
    t = TestConfigOntologyRouter()
    
    # Mock mocks
    db = MagicMock()
    repo = AsyncMock()
    
    print("\n--- Running Manual Tests ---")
    t.test_get_known_dimensions_success(db)
    
    loop = asyncio.new_event_loop()
    loop.run_until_complete(t.test_delete_dimension_success(db, repo))
    loop.run_until_complete(t.test_delete_dimension_conflict(db, repo))
    loop.run_until_complete(t.test_update_dimension_id_mismatch(db, repo))
    loop.run_until_complete(t.test_update_dimension_success(db, repo))
    print("\n--- All Manual Tests Passed ---")
