from unittest.mock import MagicMock

import pytest

from backend_v2.api.dependencies import get_llm_handler
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.llm.handler import LLMHandler


@pytest.fixture
def mock_repo() -> AbstractWorkflowRepository:
    return MagicMock(spec=AbstractWorkflowRepository)

def test_get_llm_handler_injection(mock_repo: AbstractWorkflowRepository) -> None:
    """Test that get_llm_handler correctly injects the AbstractWorkflowRepository."""
    # Act
    handler = get_llm_handler(repo=mock_repo)

    # Assert
    assert isinstance(handler, LLMHandler)
    assert handler.repo is mock_repo
    # Verify the V1 db_client logic is completely gone
    assert not hasattr(handler, "db_client")
