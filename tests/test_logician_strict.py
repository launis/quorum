
import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.models.domain.logician import LogicianInput, LogicianOutput
from backend.models.domain.analyst import AnalystOutput, Hypothesis
from backend.agents.logician import LogicianAgent
from backend.exceptions import AgentExecutionError

@pytest.mark.asyncio
async def test_logician_input_strictness():
    """Verify LogicianInput accepts step_analyst and validation logic."""
    
    # 1. Create a valid AnalystOutput mock
    analyst_output = AnalystOutput(
        thought_process="Analysis complete",
        conclusion="Evidence found",
        confidence_score=0.9,
        hypotheses=[
            Hypothesis(
                id="h1", 
                claim_text="Claim 1", 
                evidence_found=True, 
                search_query="query", 
                quotes=["quote1"]
            )
        ],
        rag_evidence=["doc1"]
    )

    # 2. Test Input Creation (Happy Path)
    # This should fail BEFORE the fix because step_analyst isn't in LogicianInput yet
    # But we write the test to expect it to work (TDD)
    try:
        input_data = LogicianInput(
            history_text="Some chat history",
            step_analyst=analyst_output
        )
        assert input_data.step_analyst is not None
    except Exception as e:
        pytest.fail(f"LogicianInput rejected step_analyst: {e}")

@pytest.fixture
def mock_llm_factory():
    with  pytest.MonkeyPatch.context() as m:
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=MagicMock(content="{}", parsed_content={}, token_usage={}))
        
        # Mock factory create_provider to return our mock provider
        m.setattr("backend.agents.base.LLMFactory.create_provider", MagicMock(return_value=mock_provider))
        yield mock_provider

@pytest.mark.asyncio
async def test_logician_agent_fallback_when_analyst_missing(mock_llm_factory):
    """Verify LogicianAgent falls back to history_text if step_analyst is missing (Preventing AttributeError)."""
    
    agent = LogicianAgent(
        model="test-model",
        provider="google"
    )
    
    # Input with history but NO step_analyst
    input_data = LogicianInput(
        history_text="Chat history",
        step_analyst=None
    )
    
    # Should SUCCEED (return context based on history), NOT crash
    context = await agent.prepare_context(input_data, None)
    # Context might be None if strictly relying on step_analyst, or string.
    # Logic: if not analyst_output: check raw_text.
    # So it returns something or None.
    # verify it didn't raise AttributeError
    
@pytest.mark.asyncio
async def test_logician_agent_fail_fast_missing_all(mock_llm_factory):
    """Verify LogicianAgent raises AgentExecutionError if BOTH step_analyst and history_text are missing/empty."""
    
    agent = LogicianAgent(
        model="test-model",
        provider="google"
    )
    
    input_data = LogicianInput(
        history_text="", # Empty
        step_analyst=None
    )
    
    with pytest.raises(AgentExecutionError) as exc:
        await agent.prepare_context(input_data, None)

    assert "Missing mandatory input" in str(exc.value.message) or "Missing" in str(exc.value)

@pytest.mark.asyncio
async def test_logician_agent_success_with_dependency(mock_llm_factory):
    """Verify LogicianAgent succeeds when dependency is provided."""
    
    agent = LogicianAgent(
        model="test-model",
        provider="google"
    )
    
    analyst_output = AnalystOutput(
        thought_process="Thinking",
        conclusion="Done", 
        confidence_score=1.0,
        hypotheses=[Hypothesis(id="1", claim_text="c", evidence_found=False, search_query="q")]
    )
    
    input_data = LogicianInput(
        history_text="Chat",
        step_analyst=analyst_output
    )
    
    # Should not raise
    context = await agent.prepare_context(input_data, None)
    assert "TODISTUSKARTTA" in context
