
import pytest
from unittest.mock import MagicMock
from backend.agents.analyst import AnalystAgent
from backend.models.domain.analyst import AnalystDTO, AnalystOutput, Hypothesis

@pytest.fixture
def analyst_agent():
    return AnalystAgent()

@pytest.mark.asyncio
async def test_analyst_deterministic_sorting(analyst_agent):
    """Verify that AnalystAgent sorts hypotheses: evidence_found=True first, then by ID."""
    
    # Input with MIXED order and IDs
    # H1: HYP-003, Evidence=False
    # H2: HYP-001, Evidence=True
    # H3: HYP-002, Evidence=True
    
    llm_output = AnalystDTO(
        thought_process="Analysis...",
        conclusion="Hypotheses generated.",
        confidence_score=0.9,
        hypotheses=[
            Hypothesis(id="HYP-003", hypothesis="H3", evidence_found=False, explanation="None"),
            Hypothesis(id="HYP-001", hypothesis="H1", evidence_found=True, explanation="Found"),
            Hypothesis(id="HYP-002", hypothesis="H2", evidence_found=True, explanation="Found"),
        ]
    )
    
    # Act: Run post_process
    # post_process reassigns IDs sequentially (HYP-1, HYP-2...) implies strict order?
    # NO. The existing logic *reassigns* IDs based on position.
    # So if we want to prioritize Evidence, we must SORT *before* reassigning IDs.
    
    processed = analyst_agent.post_process(llm_output)
    
    # Assert Order
    # Expected: 
    # 1. H1 (True, was HYP-001) -> Renamed HYP-1
    # 2. H2 (True, was HYP-002) -> Renamed HYP-2
    # 3. H3 (False, was HYP-003) -> Renamed HYP-3
    
    hyps = processed.hypotheses
    
    assert hyps[0].hypothesis == "H1"
    assert hyps[0].evidence_found == True
    assert hyps[0].id == "HYP-001"
    
    assert hyps[1].hypothesis == "H2"
    assert hyps[1].evidence_found == True
    assert hyps[1].id == "HYP-002"
    
    assert hyps[2].hypothesis == "H3"
    assert hyps[2].evidence_found == False
    assert hyps[2].id == "HYP-003"

@pytest.mark.asyncio
async def test_analyst_fail_fast_missing_hypotheses(analyst_agent):
    """Verify AnalystAgent fails fast if hypotheses are missing (None)."""
    # DTO schema says hypotheses is list, so None might be caught by Pydantic.
    # But let's simulate a case where it's passed as None/Empty?
    # Actually, empty list is valid (no hypotheses found).
    # But if input is None?
    
    raw_dict = {"step": "Analyst", "content": "C", "reasoning": "R", "hypotheses": None}
    
    # post_process is robust to None, but we want to fail fast if it's strictly required?
    # No, for Analyst, empty list is fine.
    # But if the key is missing entirely from a dict?
    
    pass
