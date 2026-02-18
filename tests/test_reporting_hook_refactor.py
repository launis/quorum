
import pytest
from unittest.mock import MagicMock
from datetime import datetime

from backend.hooks.reporting import generate_report
from backend.models.state import WorkflowState
from backend.models.domain.inputs import WorkflowInputs
from backend.models.domain.xai import XAIOutput, ReportContext
from backend.models.domain.judge import JudgeOutput, JudgeScoreCard, DimensionResultItem
from backend.models.domain.overseer import OverseerOutput, OverseerData, EthicalObservation, FactCheckRFI
from backend.models.domain.logician import LogicianOutput, LogicianData, WaltonScheme, ToulminComponent, CognitiveLevel
from backend.models.domain.performativity import PerformativityOutput, PerformativityAnalysis, PreMortemAnalysis, PerformativityHeuristic
from backend.models.enums import AuthenticityLevel, BloomLevel, StrategicDepth, FidelityLevel, AbductiveConclusion, PlausibilityLevel
from backend.models.domain.coach import BibliographyResult, BibliographyItem

def test_generate_report_success():
    # 1. Mock Inputs
    inputs = WorkflowInputs(
        history_text="User: Hello\nAI: Hi there.",
        organization_id="org-123"
    )

    # 2. Mock Agent Outputs
    
    # XAI
    score_card = JudgeScoreCard(
        agent_name="Standard Judge",
        total_score=4.5,
        max_score=5,
        verdict="Good",
        dimensions=[
            DimensionResultItem(dimension_id="dim1", dimension_label="Dim 1", score=4.5, reasoning="Good stuff")
        ],
        scale_min=1.0,
        scale_max=5.0
    )
    
    xai_out = XAIOutput(
        thought_process="Thinking...",
        conclusion="Done.",
        executive_summary="Executive Summary Text",
        analysis_strengths="Strengths",
        analysis_weaknesses="Weaknesses",
        analysis_opportunities="Opportunities",
        analysis_recommendations="Recommendations",
        final_verdict="Verdict",
        confidence_score=0.9,
        score_cards=[score_card]
    )

    # Judge (Critical Findings)
    judge_out = JudgeOutput(
        thought_process="Judging...",
        conclusion="Judged.",
        confidence_score=0.9,
        matrix_id="matrix-1",
        score_card=score_card,
        scale_min=1.0,
        scale_max=5.0,
        critical_findings=["Finding 1", "Finding 2"]
    )

    # Overseer (Ethical Issues)
    overseer_out = OverseerOutput(
        thought_process="Overseeing...",
        conclusion="Overseen.",
        confidence_score=0.9,
        overseer_data=OverseerData(
            fact_checks=[],
            ethical_issues=[
                EthicalObservation(issue_type="Bias", severity="Warning", description="Minor bias detected")
            ]
        )
    )

    # Performativity (Pre-Mortem)
    perf_out = PerformativityOutput(
        thought_process="Detecting...",
        conclusion="Detected.",
        confidence_score=0.8,
        performativity_analysis=PerformativityAnalysis(
            performativity_heuristics=[
                PerformativityHeuristic(heuristic_name="H1", flag_raised=False, description="OK")
            ],
            pre_mortem_analysis=PreMortemAnalysis(
                performed=True,
                weak_signals=["Signal 1", "Signal 2"]
            ),
            authenticity_assessment=AuthenticityLevel.ORGANIC,
            authenticity_score=3.0
        )
    )

    # Logician (Audit Questions)
    log_out = LogicianOutput(
        thought_process="Reasoning...",
        conclusion="Reasoned.",
        confidence_score=0.95,
        logician_data=LogicianData(
            toulmin_analysis=[ToulminComponent(id="t1", claim="c", data="d", warrant="w")],
            cognitive_level=CognitiveLevel(
                bloom_level=BloomLevel.ANALYZING,
                strategic_depth=StrategicDepth.HIGH,
                bloom_score=4.0,
                strategic_score=3.0
            ),
            walton_scheme=WaltonScheme(
                identified_scheme="Scheme A",
                critical_questions=["Q1", "Q2"]
            ),
            toulmin_score=3.0
        )
    )

    # Bibliography
    bib_res = BibliographyResult(
        references=[
            BibliographyItem(source_id="s1", title="Source 1")
        ]
    )

    # 3. Construct WorkflowState
    state = WorkflowState(
        workflow_id="test-flow",
        context_variables={
            "inputs": inputs,
            "step_xai": xai_out,
            "step_judge": judge_out,
            "step_overseer": overseer_out,
            "step_detector": perf_out,
            "step_logician": log_out,
            "bibliography_result": bib_res
        }
    )

    # 4. Run Hook
    new_state = generate_report(state)

    # 5. Assertions
    ctx = new_state.context_variables.get("report_context")
    assert ctx is not None
    assert isinstance(ctx, dict)
    
    # Check mapped fields
    assert ctx["summary"] == "Executive Summary Text"
    assert ctx["critical_findings"] == ["Finding 1", "Finding 2"]
    assert ctx["pre_mortem_signals"] == ["Signal 1", "Signal 2"]
    assert len(ctx["ethical_issues"]) == 1
    assert ctx["ethical_issues"][0]["issue_type"] == "Bias"
    assert len(ctx["audit_questions"]) == 2
    assert ctx["audit_questions"][0]["question"] == "Q1"
    # Check Score Parsing
    # The hook parses xai_out.score_cards[0].dimensions[0] => "dim1"
    # ctx["scores"] should be dict[str, dict]
    assert "dim1" in ctx["scores"]
    assert ctx["scores"]["dim1"]["arvosana"] == 4.5
    
    assert ctx["average_score"] == 4.5
    assert len(ctx["bibliography"]) == 1
    assert ctx["bibliography"][0]["source_id"] == "s1"
    
    print("Report Context generated successfully with full mapping!")

def test_generate_report_fail_fast_missing_inputs():
    state = WorkflowState(workflow_id="test-fail", context_variables={})
    # fast failure on inputs
    with pytest.raises(Exception) as exc:
        generate_report(state)
    assert "Missing 'inputs'" in str(exc.value)

def test_generate_report_fallback_minimal():
    """Test that report handles missing agent outputs gracefully (defaults)."""
    inputs = WorkflowInputs(history_text="...", organization_id="1")
    state = WorkflowState(workflow_id="test-fallback", context_variables={"inputs": inputs})
    
    new_state = generate_report(state)
    ctx = new_state.context_variables.get("report_context")
    
    assert ctx["summary"] == "No Executive Summary available (XAI Agent did not run or failed)."
    assert ctx["critical_findings"] == []
    assert ctx["scores"] == {}
    assert ctx["average_score"] == 0.0
    assert ctx["bibliography"] == []
    
    print("Report Context generated successfully with minimal context!")
