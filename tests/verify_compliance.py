
import logging
import sys
import os

# Ensure backend matches path
sys.path.append(os.getcwd())

from backend.models.state import WorkflowState
from backend.models.domain.analyst import AnalystOutput, Hypothesis
from backend.models.domain.overseer import OverseerOutput, OverseerData, FactCheckRFI, EthicalObservation
from backend.models.domain.performativity import PerformativityOutput, PerformativityAnalysis
from backend.models.domain.judge import JudgeOutput, JudgeScoreCard, DimensionResultItem
from backend.models.enums import AuthenticityLevel

from backend.hooks.integrity import verify_citation_integrity
from backend.hooks.scoring import apply_scoring_logic, enforce_scoring_penalties

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_integrity_hook():
    logger.info("Testing Integrity Hook...")
    
    # 1. Setup Context
    analyst_out = AnalystOutput(
        hypotheses=[
            Hypothesis(
                id="HYP-1", 
                claim_text="Test Claim", 
                evidence_found=True, 
                search_query="query", 
                quotes=["valid quote"]
            )
        ],
        rag_evidence=["valid quote"],
        critical_violation=False,
        thought_process="Thinking...",
        conclusion="Conclusion.",
        confidence_score=1.0
    )
    
    state = WorkflowState(
        workflow_id="test_workflow",
        context_variables={
            "inputs": {"history_text": "valid quote", "product_text": "", "reflection_text": ""},
            "step_analyst": analyst_out
        }
    )
    
    # 2. Run Hook
    try:
        new_state = verify_citation_integrity(state)
        # Note: If no previous integrity_audit exists, hook might not create it in context_variables directly 
        # but inside metadata['audit_logs']. 
        # However, looking at integrity.py: new_context["integrity_audit"] = audit
        audit = new_state.context_variables.get("integrity_audit")
        
        if audit and audit.integrity_score == 1.0:
            logger.info("Integrity Hook Passed (Valid Citation).")
        else:
            # If we pass valid quote, it should match "valid quote" in history.
            logger.error(f"Integrity Hook Failed: Score {audit.integrity_score if audit else 'None'}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Integrity Hook Exception: {e}")
        sys.exit(1)

def test_scoring_hook():
    logger.info("Testing Scoring Hook...")
    
    # Setup Inputs
    judge_out = JudgeOutput(
        score_card=JudgeScoreCard(
            agent_name="Standard Judge",
            total_score=4.0,
            max_score=4,
            scale_min=1.0,
            scale_max=4.0,
            dimensions=[
                DimensionResultItem(dimension_id="d1", dimension_label="Dim1", score=4.0, reasoning="Good"),
                DimensionResultItem(dimension_id="d2", dimension_label="Dim2", score=4.0, reasoning="Good")
            ],
            verdict="Excellent"
        ),
        scale_min=1.0,
        scale_max=4.0,
        critical_findings=[],
        reasoning_trace="Initial Trace", # inherited field overrides? No, check base.
        # ReasoningTrace has thought_process, conclusion, confidence_score.
        # JudgeOutput inherits ReasoningTrace.
        # Wait, definitions in judge.py: class JudgeOutput(ReasoningTrace): ...
        
        thought_process="Judging...",
        conclusion="Excellent result.",
        confidence_score=1.0
    )
    
    # Case A: Normal (No Penalties)
    state = WorkflowState(
        workflow_id="test_workflow",
        context_variables={
            "step_judge": judge_out,
            # No guard/falsifier inputs = No penalties
        }
    )
    
    new_state = apply_scoring_logic(state)
    res = new_state.context_variables["step_judge"]
    if res.score_card.total_score == 4.0:
        logger.info("Scoring Hook Passed (No Penalties).")
    else:
        logger.error(f"Scoring Hook Failed (Normal): {res.score_card.total_score}")
        sys.exit(1)

    # Case B: Security Threat (Legacy Dict Simulation + Guard)
    # We simulate a Guard output using a dict to test _inflate or dict access in hook
    # Actually hook uses strict access for Guard? No, hook used specific parsing for Guard.
    # Let's use a dict for guard to verify robustness.
    
    state_threat = WorkflowState(
        workflow_id="test_workflow",
        context_variables={
            "step_judge": judge_out,
            "step_guard": {"security_check": {"uhka_havaittu": True}} # Supported by hook legacy check
        }
    )
    
    new_state_threat = apply_scoring_logic(state_threat)
    res_threat = new_state_threat.context_variables["step_judge"]
    if res_threat.score_card.total_score == 1.0:
        logger.info("Scoring Hook Passed (Security Penalty Applied).")
    else:
        logger.error(f"Scoring Hook Failed (Security): {res_threat.score_card.total_score}")
        sys.exit(1)

def test_net_negligence():
    logger.info("Testing Net Negligence (Reporting)...")
    
    # Setup Inputs
    analyst_out = AnalystOutput(
        hypotheses=[Hypothesis(id="HYP-1", claim_text="C", evidence_found=True, search_query="q", quotes=["q"])],
        critical_violation=True, # ! Violation
        thought_process="Thinking...",
        conclusion="Conclusion.",
        confidence_score=1.0
    )
    
    overseer_out = OverseerOutput(
        overseer_data=OverseerData(
            fact_checks=[
                FactCheckRFI(claim="c", verification_result="Debunked", source_or_reasoning="s") # ! Hallucination
            ],
            ethical_issues=[]
        ),
        thought_process="Overseeing...",
        conclusion="Done.",
        confidence_score=1.0
    )
    
    detector_out = PerformativityOutput(
        performativity_analysis=PerformativityAnalysis(
            performativity_heuristics=[],
            pre_mortem_analysis={"performed":True, "weak_signals":[]}, # Pydantic might cast this if defined as model field
            authenticity_assessment=AuthenticityLevel.PERFORMATIVE, # ! Say-Do Gap
            authenticity_score=2.0
        ),
        thought_process="Detecting...",
        conclusion="Done.",
        confidence_score=1.0
    )
    
    input_data = {
        "step_analyst": analyst_out,
        "step_overseer": overseer_out,
        "step_detector": detector_out
    }
    
    result_obj = {"critical_findings": [], "reasoning_trace": "", "score_card": {"verdict": "Initial"}}
    
    new_result = enforce_scoring_penalties(result_obj, input_data)
    
    findings = new_result["critical_findings"]
    
    expected = [
        "[KRUUNUNJALOKIVI] TIETOPANKKIRIKKOMUS (Critical Violation)",
        "[HALLUSINAATIO] 1 kpl korjaamatta (Uncorrected Hallucinations)",
        "[FORENSIIKKA] Say-Do Gap (Illusion of Control)"
    ]
    
    missing = [e for e in expected if e not in findings]
    
    if not missing:
        logger.info("Net Negligence Reporting Passed.")
    else:
        logger.error(f"Net Negligence Failed. Missing: {missing}. Got: {findings}")
        sys.exit(1)

if __name__ == "__main__":
    test_integrity_hook()
    test_scoring_hook()
    test_net_negligence()
    logger.info("ALL COMPLIANCE TESTS PASSED.")
