
import pytest
from unittest.mock import MagicMock
from backend.agents.coach import CoachAgent
from backend.models.domain.coach import CoachingPlanDTO, CoachingPlan

@pytest.fixture
def coach_agent():
    return CoachAgent()

@pytest.mark.asyncio
async def test_coach_deduplication(coach_agent):
    """Verify that CoachAgent removes duplicates from bibliography and actionable_steps."""
    
    # Input with DUPLICATES
    llm_output = CoachingPlanDTO(
        thought_process="Thinking step-by-step...",
        conclusion="Here is the plan.",
        confidence_score=1.0,
        # Duplicate Steps
        actionable_steps=[
            "Do X.",
            "Do Y.",
            "Do X.", # Duplicate
            "Do Z."
        ],
        # Duplicate Bibliography
        bibliography=[
            {"title": "Ref A", "url": "http://a.com", "source_id": "1"},
            {"title": "Ref B", "url": "http://b.com", "source_id": "2"},
            {"title": "Ref A", "url": "http://a.com", "source_id": "1"} # Duplicate
        ],
        focus_areas=["Area 1"]
    )
    
    # Act: Run post_process
    # We need to implement the deduplication logic in post_process.
    
    processed = coach_agent.post_process(llm_output)
    
    # Assert Deduplication
    steps = processed.actionable_steps
    bib = processed.bibliography
    
    assert len(steps) == 3
    assert steps.count("Do X.") == 1
    
    assert len(bib) == 2
    titles = [b["title"] for b in bib]
    assert titles.count("Ref A") == 1

@pytest.mark.asyncio
async def test_coach_fail_fast_empty_steps(coach_agent):
    """Verify CoachAgent fails fast if actionable_steps is empty."""
    
    # Use a DICT to simulate raw LLM output before Pydantic validation
    # This allows us to pass "invalid" data to post_process to verify IT catches it.
    raw_output = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "actionable_steps": [], # EMPTY
        "bibliography": [],
        "focus_areas": ["Area 1"]
    }
    
    from backend.exceptions import AgentExecutionError, ErrorCodes
    
    with pytest.raises(AgentExecutionError) as exc:
        coach_agent.post_process(raw_output)
        
    assert exc.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA.value
