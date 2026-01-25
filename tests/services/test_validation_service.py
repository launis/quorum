from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.validation_service import WorkflowValidator


@pytest.mark.asyncio
async def test_validate_flow_configuration_success():
    # Mock Registry
    mock_registry = AsyncMock()
    mock_registry.resolve_model_config.return_value = {"model_name": "gpt-4"}

    # Mock AgentFactory
    with patch("backend.services.validation_service.AgentFactory") as MockFactory:
        # returns map of agent_name -> AgentInstance
        mock_agent = MagicMock()
        mock_agent.REQUIRES_KEYS = []
        mock_agent.PRODUCES_KEYS = ["result"]

        MockFactory.create_agents_map.return_value = {
            "test_agent": mock_agent
        }

        # Test Data
        sequence = ["step1"]
        steps_db_map = {
            "step1": {"id": "step1", "component": "test_agent"}
        }

        result = await WorkflowValidator.validate_flow_configuration(sequence, steps_db_map, mock_registry)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

@pytest.mark.asyncio
async def test_validate_flow_configuration_unknown_step():
    # Mock Registry
    mock_registry = AsyncMock()
    mock_registry.resolve_model_config.return_value = {"model_name": "gpt-4"}

    with patch("backend.services.validation_service.AgentFactory") as MockFactory:
        MockFactory.create_agents_map.return_value = {}

        sequence = ["step1"]
        from typing import Any
        steps_db_map: dict[str, Any] = {} # Empty

        result = await WorkflowValidator.validate_flow_configuration(sequence, steps_db_map, mock_registry)

        assert result["valid"] is False
        assert "Unknown Step: step1" in result["errors"]
