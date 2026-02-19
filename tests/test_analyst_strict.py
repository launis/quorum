
import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.models.domain.analyst import AnalystInput, AnalystOutput
from backend.agents.analyst import AnalystAgent
from backend.exceptions import AgentExecutionError

@pytest.fixture
def mock_llm_factory():
    with pytest.MonkeyPatch.context() as m:
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=MagicMock(content="{}", parsed_content={}, token_usage={}))
        
        # Mock factory create_provider to return our mock provider
        m.setattr("backend.agents.base.LLMFactory.create_provider", MagicMock(return_value=mock_provider))
        yield mock_provider

@pytest.mark.asyncio
async def test_analyst_fail_fast_short_input(mock_llm_factory):
    """Verify AnalystAgent raises AgentExecutionError if history_text is too short."""
    
    agent = AnalystAgent(
        model="test-model",
        provider="google"
    )
    
    # Input too short (< 100 chars)
    input_data = AnalystInput(
        history_text="Short text",
        product_text=None,
        reflection_text=None
    )
    
    with pytest.raises(AgentExecutionError) as exc:
        await agent.execute(input_data)
        
    assert "Input 'history_text' is too short" in str(exc.value.message) or "too short" in str(exc.value)

@pytest.mark.asyncio
async def test_analyst_success_valid_input(mock_llm_factory):
    """Verify AnalystAgent succeeds with valid input."""
    
    agent = AnalystAgent(
        model="test-model",
        provider="google"
    )
    
    # Input sufficiently long
    input_data = AnalystInput(
        history_text="Long enough text " * 20, # > 100 chars
        product_text=None,
        reflection_text=None
    )
    
    # Should not raise
    await agent.execute(input_data, system_instruction="Analyze this.")
