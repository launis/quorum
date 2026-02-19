
import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.models.domain.falsifier import FalsifierInput, FalsifierOutput
from backend.models.domain.analyst import AnalystOutput, Hypothesis
from backend.agents.critics import LogicalFalsifierAgent
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
async def test_falsifier_fail_fast_missing_dependency(mock_llm_factory):
    """Verify LogicalFalsifierAgent raises AgentExecutionError if step_analyst is missing."""
    
    agent = LogicalFalsifierAgent(
        model="test-model",
        provider="google"
    )
    
    # Missing step_analyst
    input_data = FalsifierInput(
        history_text="Some history",
        step_analyst=None
    )
    
    with pytest.raises(AgentExecutionError) as exc:
        await agent.execute(input_data)
        
    assert "Mandatory input 'step_analyst' missing" in str(exc.value.message) or "missing" in str(exc.value)

@pytest.mark.asyncio
async def test_falsifier_success_with_dependency(mock_llm_factory):
    """Verify LogicalFalsifierAgent succeeds when dependency is provided."""
    
    agent = LogicalFalsifierAgent(
        model="test-model",
        provider="google"
    )
    
    analyst_output = AnalystOutput(
        thought_process="Thinking",
        conclusion="Done", 
        confidence_score=1.0,
        hypotheses=[
            Hypothesis(id="h1", claim_text="Claim", evidence_found=True, search_query="q")
        ]
    )
    
    input_data = FalsifierInput(
        history_text="Some history",
        step_analyst=analyst_output
    )
    
    # Should not raise
    await agent.execute(input_data, system_instruction="Falsify this.")
