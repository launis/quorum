
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.agents.coach import CoachAgent
from backend.models.domain import CoachInput, CoachingPlan, CoachingPlanDTO, Metadata
from backend.exceptions import AgentExecutionError

@pytest.fixture
def mock_llm_factory():
    with pytest.MonkeyPatch.context() as m:
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=MagicMock(content="{}", parsed_content={}, token_usage={}))
        m.setattr("backend.agents.base.LLMFactory.create_provider", MagicMock(return_value=mock_provider))
        yield mock_provider

@pytest.mark.asyncio
async def test_coach_strict_dto_usage(mock_llm_factory):
    """Verify CoachAgent uses DTO and promotes to Domain Model with Metadata."""
    agent = CoachAgent(model="test-model", provider="google")
    
    # Mock LLM returning DTO content
    mock_dto = CoachingPlanDTO(
        thought_process="Thinking...",
        conclusion="Conclusion...",
        confidence_score=0.9,
        actionable_steps=["Step 1"],
        bibliography=[],
        focus_areas=["Area 1"]
    )
    mock_llm_factory.generate.return_value.parsed_content = mock_dto
    
    input_data = CoachInput(
        history_text="History",
        step_judge={"verdict": "Guilty"}, # Minimal mock
        last_reasoning_trace=None
    )
    
    # Mock Repository for enrichment (Coach needs it)
    mock_repo = MagicMock()
    mock_repo.get_knowledge_base_items = AsyncMock(return_value=[])
    
    result = await agent.execute(
        input_data, 
        execution_context={"repository": mock_repo},
        system_instruction="Coach me."
    )
    
    # Verify Result Type
    assert isinstance(result, CoachingPlan)
    
    # Verify Content (mapped from DTO)
    assert result.actionable_steps == ["Step 1"]
    
    # Verify Metadata (Injected by BaseAgent)
    assert result.metadata is not None
    assert isinstance(result.metadata, Metadata)
    assert result.metadata.agentti == "CoachAgent"
    assert result.metadata.luontiaika is not None
    
    # Verify LLM was called with DTO schema
    call_kwargs = mock_llm_factory.generate.call_args.kwargs
    assert call_kwargs["response_schema"] == CoachingPlanDTO
    
@pytest.mark.asyncio
async def test_coach_fail_fast_missing_dependency(mock_llm_factory):
    """Test Fail Fast when step_judge is missing."""
    agent = CoachAgent(model="test-model", provider="google")
    
    # Missing step_judge implies empty dict or None in input if allowed, 
    # but CoachInput defines it as ... (Required).
    # so we test providing Empty Dict if Pydantic allows?
    # Actually CoachInput requires step_judge field.
    # But inside execute -> prepare_context, it checks if it's "truthy"?
    
    # CoachInput(step_judge={}) is valid Pydantic, but logic inside might check content.
    # To skip the step_judge check and hit the repository check,
    # we need to provide a non-empty step_judge.
    input_data = CoachInput(
        history_text="History",
        step_judge={"verdict": "Guilty", "score": 1}, # Non-empty
        last_reasoning_trace=None
    )
     
    # Logic in prepare_context:
    # for key, value in input_dict.items():
    #      if key.startswith("step_judge") and value:
    #          judge_inputs.append((key, value))
    # if not judge_inputs: raise...
    
    # So empty dict should trigger fail fast if it relies on value being truthy?
    # Let's see. step_judge={} is truthy? Yes.
    # But judge_inputs.append...
    # Wait, loop iterates input_dict items.
    # key="step_judge", value={} -> Truthy? Yes.
    
    # Actually, let's look at the code again.
    # It loops over startsWith("step_judge").
    
    # Let's try passing None if we can bypass Pydantic... we can't easily.
    # But if we pass a dict that is empty?
    
    # Let's test missing repository instead, easier to trigger.
    
    with pytest.raises(ValueError) as exc:
        CoachInput(
            history_text="History",
            step_judge={}, # Falsy Empty
            step_judge_cognitive={}, # Falsy Empty
            last_reasoning_trace=None
        )
    
    assert "CoachAgent requires at least one judge input" in str(exc.value)
