from backend.api.transformers.domain.causal import CausalDomainTransformer
from backend.api.transformers.domain.compliance import ComplianceDomainTransformer
from backend.api.transformers.domain.falsification import FalsificationDomainTransformer
from backend.api.transformers.domain.logic import LogicDomainTransformer
from backend.api.transformers.domain.profiling import ProfilingDomainTransformer

# Deprecated: backend.models.view_extensions
from backend.models.state import WorkflowState
from backend.models.view import (
    SectionType,
    UiSection,
)
from backend.models.view.semantic_models import (
    ArchivistDisplay,
    CausalDisplay,
    DriverProfileDisplay,
    LogicAnalysisDisplay,
    PerformativityDisplay,
    ProfilerDisplay,
    StressTestDisplay,
)
from backend.models.view.semantic_models import SemanticBlock


# --- Logic Transformer Tests ---
def test_logic_transformer_extracts_display_model():
    transformer = LogicDomainTransformer()
    mock_step_data = {
        "logician_data": {
            "cognitive_level": {
                "strategic_depth": "STRAT_HIGH",
                "strategic_score": 3.5,
                "bloom_level": "BLOOM_EVALUATING",
                "bloom_score": 5.8,
            },
            "toulmin_score": 5.0,
            "toulmin_analysis": [{"id": "T1", "claim": "C1", "data": "D1", "warrant": "W1"}],
            "walton_scheme": {"identified_scheme": "Expert Opinion", "critical_questions": ["Q1"]},
        },
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9,
    }

    mock_state = WorkflowState(workflow_id="test_wf")
    mock_state.context_variables["step_logician"] = mock_step_data

    section = transformer._extract_logician_section(mock_state)
    assert isinstance(section, SemanticBlock)
    assert section.id == "logic-analysis"
    assert isinstance(section.value, LogicAnalysisDisplay)
    assert section.value.strategic_score == 3.5
    assert section.value.bloom_score == 5.8
    assert len(section.value.arguments) == 1


def test_logic_transformer_handles_missing_step():
    transformer = LogicDomainTransformer()
    mock_state = WorkflowState(workflow_id="test_wf")
    section = transformer._extract_logician_section(mock_state)
    assert section is None


# --- Stress Transformer Tests ---
def test_stress_transformer_extracts_display_model():
    transformer = FalsificationDomainTransformer()
    mock_step_data = {
        "falsifier_data": {
            "fidelity_audit": {
                "fidelity_score": "FIDELITY_HIGH",
                "fidelity_numeric": 2.9,
                "justification": "Solid",
                "post_hoc_rationalization": False,
            },
            "stress_test_findings": [{"question": "Q1", "evidence_held": True, "observation": "Obs1"}],
        },
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9,
    }

    mock_state = WorkflowState(workflow_id="test_wf")
    mock_state.context_variables["step_falsifier"] = mock_step_data

    section = transformer._extract_falsifier_section(mock_state)
    assert isinstance(section, SemanticBlock)
    assert section.id == "stress-test"
    assert isinstance(section.value, StressTestDisplay)
    assert section.value.fidelity_audit is not None
    assert section.value.fidelity_audit.fidelity_label == "FIDELITY_HIGH"
    assert len(section.value.findings) > 0
    assert section.value.findings[0].result_label == "VER_HELD"


# --- Causal Transformer Tests ---
def test_causal_transformer_extracts_display_model():
    transformer = CausalDomainTransformer()
    mock_step_data = {
        "causal_analysis": {
            "abductive_reasoning": {"verdict": "OK", "confidence_score": 0.9, "conclusion": "Conc1"},
            "abductive_conclusion": "GENUINE",
            "abductive_score": 3.0,
            "counterfactual_test": {
                "plausibility": "PLAUSIBLE",
                "confidence_score": 0.8,
                "actual_scenario": "A1",
                "simulated_scenario": "S1",
                "plausibility_score": "PLAUSIBLE",
                "plausibility_numeric": 2.0,
                "simulation_result": "SimResult",
            },
            "plausibility_check": {"score": 2.5},
            "observation": "Obs1",
            "hypothesis": "Hyp1",
        },
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9,
    }

    mock_state = WorkflowState(workflow_id="test_wf")
    mock_state.context_variables["step_causal"] = mock_step_data

    section = transformer._extract_causal_section(mock_state)
    assert isinstance(section, SemanticBlock)
    assert section.id == "causal-analysis"
    assert isinstance(section.value, CausalDisplay)
    assert section.value.abductive_score_display == "3.0"
    assert section.value.plausibility_score_display == "2.0"


# --- Profiler Transformer Tests ---
def test_profiler_transformer_extracts_display_model():
    transformer = ProfilingDomainTransformer()
    mock_step_data = {
        "metrics": {
            "control_ratio": 0.6,
            "word_count": 100,
            "avg_sentence_length": 10.0,
            "sentence_count": 10,
            "lexical_diversity": 0.5,
            "capitalization_ratio": 0.1,
            "automation_bias": 0.1,
            "say_do_gap": 0.9,
        },
        "author_intent": "Info",
        "emotional_tone": "Neutral",
        "cognitive_biases": ["Bias1"],
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9,
    }

    mock_state = WorkflowState(workflow_id="test_wf")
    mock_state.context_variables["step_profiler"] = mock_step_data

    section = transformer._extract_profiler_section(mock_state)
    assert isinstance(section, SemanticBlock)
    assert section.id == "profiler-analysis"
    assert isinstance(section.value, ProfilerDisplay)
    # Check hoisted thresholds
    assert section.value.automation_bias_color == "green"  # 0.1 < threshold (0.5) -> Green
    assert section.value.say_do_gap_color == "red"  # 0.9 > threshold


# --- Detector Transformer Tests (in Profiling) ---
def test_detector_transformer_extracts_display_model():
    transformer = ProfilingDomainTransformer()
    mock_step_data = {
        "performativity_analysis": {
            "authenticity_score": 2.5,
            "authenticity_assessment": "AUTH_ORGANIC",
            "performativity_heuristics": [{"heuristic_name": "H1", "flag_raised": True, "description": "Desc1"}],
            "pre_mortem_analysis": {"performed": True, "weak_signals": ["Signal1"]},
        },
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9,
    }

    mock_state = WorkflowState(workflow_id="test_wf")
    mock_state.context_variables["step_detector"] = mock_step_data

    section = transformer._extract_detector_section(mock_state)
    assert isinstance(section, SemanticBlock)
    assert section.id == "performativity-check"
    assert isinstance(section.value, PerformativityDisplay)
    assert section.value.authenticity_score == 2.5
    assert section.value.heuristics[0].name == "H1"
    assert section.value.heuristics[0].color == "red"


# --- Driver Transformer Tests (in Profiling) ---
def test_driver_transformer_extracts_display_model():
    transformer = ProfilingDomainTransformer()
    mock_step_data = {
        "role_classification": "Driver",
        "high_dependency": False,
        "imperative_command_count": 2,
        "strategy": "Zero-shot",
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9,
    }

    mock_state = WorkflowState(workflow_id="test_wf")
    mock_state.context_variables["step_interaction"] = mock_step_data

    section = transformer._extract_interaction_section(mock_state)
    assert isinstance(section, SemanticBlock)
    assert section.id == "interaction-grid"
    assert isinstance(section.value, DriverProfileDisplay)
    assert section.value.role_classification == "ROLE_DRIVER"


# --- Archivist Transformer Tests (in Compliance) ---
def test_archivist_transformer_extracts_display_model():
    transformer = ComplianceDomainTransformer()
    mock_step_data = {
        "compliance_score": 4.0,
        "compliance_analysis": "Aligned",
        "description": "Good",
        "relevant_cases": [{"case_id": "C1", "summary": "Sum1", "similarity_score": 0.9, "verdict": "V1"}],
        "stare_decisis_adherence": True,
        "consistency_analysis": "Consistent",
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9,
    }

    mock_state = WorkflowState(workflow_id="test_wf")
    mock_state.context_variables["step_archivist"] = mock_step_data

    section = transformer._extract_archivist_section(mock_state)
    assert isinstance(section, SemanticBlock)
    assert section.id == "archivist-check"
    assert isinstance(section.value, ArchivistDisplay)
    assert section.value.compliance_score == 4.0
