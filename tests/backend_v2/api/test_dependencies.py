from unittest.mock import MagicMock

import pytest

from backend_v2.api.dependencies import get_llm_handler
from backend_v2.database.interfaces import IWorkflowRepository
from backend_v2.llm.handler import LLMHandler


@pytest.fixture
def mock_repo() -> IWorkflowRepository:
    return MagicMock(spec=IWorkflowRepository)

def test_get_llm_handler_injection(mock_repo: IWorkflowRepository) -> None:
    """Test that get_llm_handler correctly injects the AbstractWorkflowRepository."""
    # Act
    handler = get_llm_handler(repo=mock_repo)

    # Assert
    assert isinstance(handler, LLMHandler)
    assert handler.repo is mock_repo
    # Verify the V1 db_client logic is completely gone
    assert not hasattr(handler, "db_client")
