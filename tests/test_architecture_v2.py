import pytest
import logging
from unittest.mock import MagicMock, patch
from backend.hooks.reporting import generate_report
from backend.models.state import WorkflowState
from backend.models.domain import EvaluationResult, Pisteet, PisteetKriteeri, XAIReport
from typing import Optional

# Setup Mock State classes to simulate Pydantic behavior
class MockStep(EvaluationResult):
    pass

def test_reporting_dual_comparison():
    """
    Test that generate_report correctly identifies two evaluation steps
    and generates 'comparison_data' (V2 Logic).
    """
    # 1. Create State with TWO judges
    p1 = Pisteet(
        analyysi=PisteetKriteeri(arvosana=8.0, perustelu="Good analysis"),
        arviointi=PisteetKriteeri(arvosana=7.0, perustelu="Decent eval"),
        synteesi=PisteetKriteeri(arvosana=6.0, perustelu="Okay syn")
    )
    s1 = MockStep(pisteet=p1, metadata={"agentti": "Judge 1"})

    p2 = Pisteet(
        analyysi=PisteetKriteeri(arvosana=9.0, perustelu="Better analysis"),
        arviointi=PisteetKriteeri(arvosana=7.0, perustelu="Same eval"),
        synteesi=PisteetKriteeri(arvosana=8.0, perustelu="Improved syn")
    )
    s2 = MockStep(pisteet=p2, metadata={"agentti": "Judge 2"})
    
    # Initialize state
    state = WorkflowState(
        step_judge=s1,
        step_judge_cognitive=s2,
        step_reporter=XAIReport(
            executive_summary="Test Summary",
            analysis_strengths="Strength",
            analysis_weaknesses="Weakness",
            analysis_opportunities="Opportunity",
            analysis_recommendations="Recs",
            final_verdict="Pass",
            confidence_score=0.9
        )
    )

    # 2. Run Hook
    new_state = generate_report(state)
    
    # 3. Assertions
    rep = new_state.step_reporter
    assert rep.comparison_data is not None, "Comparison data missing in dual mode"
    assert rep.comparison_data['mode'] == 'dual'
    
    # Check Delta calculation 
    # Logic: Sorted by attr name. step_judge < step_judge_cognitive.
    # Left = step_judge (8), Right = step_judge_cognitive (9).
    # Delta = R - L = 9 - 8 = +1.
    
    row_analysis = next(r for r in rep.comparison_data['rows'] if r['dimension'] == 'analyysi')
    assert row_analysis['delta'] == 1.0
    assert row_analysis['left']['score'] == 8.0
    assert row_analysis['right']['score'] == 9.0

def test_reporting_single_judge_fallback():
    """
    Test that generate_report handles single judge correctly (no comparison data).
    """
    p1 = Pisteet(analyysi=PisteetKriteeri(arvosana=8.0, perustelu="Solo"))
    s1 = MockStep(pisteet=p1, metadata={"agentti": "Solo Judge"})
    
    state = WorkflowState(
        step_judge=s1,
        step_reporter=XAIReport(
            executive_summary="Test",
            analysis_strengths="S", analysis_weaknesses="W", 
            analysis_opportunities="O", analysis_recommendations="R",
            final_verdict="Pass", confidence_score=0.9
        )
    )
    
    new_state = generate_report(state)
    rep = new_state.step_reporter
    
    assert rep.comparison_data is None, "Simulated Single Judge should not have comparison data"
