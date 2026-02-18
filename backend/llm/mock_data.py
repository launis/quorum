"""Mock Data Store for AI Layer Testing (Zero-Token Cost)."""

from datetime import datetime
from typing import Any

from backend.models.domain import (
    AnalystOutput,
    ArchiveCase,
    ArchivistOutput,
    CausalAnalysis,
    CausalOutput,
    CoachingPlan,
    CognitiveLevel,
    CounterfactualTest,
    DimensionResultItem,
    EthicalObservation,
    EvaluationResult,
    FactCheckRFI,
    FalsifierData,
    FalsifierOutput,
    GuardOutput,
    Hypothesis,
    InteractionAnalysis,
    JudgeScoreCard,
    LogicianData,
    # Output Models
    LogicianOutput,
    Metadata,
    OverseerData,
    OverseerOutput,
    PanelOutput,
    PerformativityAnalysis,
    PerformativityHeuristic,
    PerformativityOutput,
    PreMortemAnalysis,
    ProfilerAnalysis,
    ReasoningFidelity,
    SecurityCheck,
    TaintedDataContent,
    ToulminComponent,
    WaltonScheme,
    WaltonStressTest,
    XAIOutput,
)
from backend.models.enums import (
    AbductiveConclusion,
    AuthenticityLevel,
    BloomLevel,
    FidelityLevel,
    PlausibilityLevel,
    RiskLevel,
    SimulationType,
    StrategicDepth,
)

# 0. Shared Metadata
MOCK_METADATA = Metadata(
    luontiaika=datetime.now(),
    agentti="MockAgent",
    vaihe=1,
    versio="1.0",
    suoritus_ymparisto="Testing"
)

# 1. Analyst Agent
MOCK_ANALYST_OUTPUT = AnalystOutput(
    # reasoning_trace removed
    thought_process="Analyst Thinking Process: Reviewing claims against known patterns.",
    conclusion="Analyst Conclusion: The text contains verifiable claims.",
    confidence_score=0.9,
    metadata=MOCK_METADATA.model_copy(update={"agentti": "AnalystAgent", "vaihe": 2}),
    hypotheses=[
        Hypothesis(
            id="hyp-1",
            claim_text="Mock Claim 1",
            evidence_found=True,
            search_query="mock query",
            quotes=["quote 1"]
        )
    ],
    rag_evidence=["Evidence 1"]
)

# ... (Panel Components) ...

MOCK_LOGICIAN_DATA = LogicianData(
    toulmin_analysis=[
        ToulminComponent(
            id="toul-1",
            claim="Toulmin Claim",
            data="Data",
            warrant="Warrant"
        )
    ],
    cognitive_level=CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=4.0,
        strategic_score=3.0,
        description="Analyzing High"
    ),
    walton_scheme=WaltonScheme(
        identified_scheme="Expert Opinion",
        critical_questions=["Expert credible?"]
    ),
    toulmin_score=4.0,
    description="Logician Analysis"
)

MOCK_LOGICIAN_OUTPUT = LogicianOutput(
    thought_process="Mock Logician Trace: Analyzed logic.",
    conclusion="Logically sound.",
    confidence_score=0.9,
    logician_data=MOCK_LOGICIAN_DATA
)

MOCK_FALSIFIER_DATA = FalsifierData(
    stress_test_findings=[
        WaltonStressTest(
            question="Stress Question 1",
            evidence_held=True,
            observation="Observed pass"
        )
    ],
    fidelity_audit=ReasoningFidelity(
        is_post_hoc=False,
        justification="Sound reasoning",
        fidelity_score=FidelityLevel.HIGH,
        fidelity_numeric=3.0
    )
)

MOCK_FALSIFIER_OUTPUT = FalsifierOutput(
    thought_process="Mock Falsifier Trace: Checked for hidden variables.",
    conclusion="No major falsifiers found.",
    confidence_score=0.9,
    falsifier_data=MOCK_FALSIFIER_DATA
)

MOCK_CAUSAL_ANALYSIS = CausalAnalysis(
    observation="Valid timeline",
    hypothesis="Test Hypothesis",
    counterfactual_test=CounterfactualTest(
        actual_scenario="A",
        simulation_result="B",
        plausibility_score=PlausibilityLevel.PLAUSIBLE,
        plausibility_numeric=2.0
    ),
    abductive_conclusion=AbductiveConclusion.GENUINE,
    abductive_score=3.0
)

MOCK_CAUSAL_OUTPUT = CausalOutput(
    thought_process="Mock Causal Trace: Verified causality.",
    conclusion="Causal link established.",
    confidence_score=0.85,
    causal_analysis=MOCK_CAUSAL_ANALYSIS
)

MOCK_PERFORMATIVITY_ANALYSIS = PerformativityAnalysis(
    performativity_heuristics=[
        PerformativityHeuristic(
            heuristic_name="H1",
            flag_raised=False,
            description="No flags"
        )
    ],
    pre_mortem_analysis=PreMortemAnalysis(
        performed=True,
        weak_signals=["Signal 1"]
    ),
    authenticity_assessment=AuthenticityLevel.ORGANIC,
    authenticity_score=3.0
)

MOCK_PERFORMATIVITY_OUTPUT = PerformativityOutput(
    thought_process="Mock Performativity Trace: Analyzed linguistics.",
    conclusion="Organic content detected.",
    confidence_score=0.9,
    performativity_analysis=MOCK_PERFORMATIVITY_ANALYSIS
)

MOCK_OVERSEER_DATA = OverseerData(
    fact_checks=[
        FactCheckRFI(
            claim="Fact Check Claim 1",
            verification_result="Verified",
            source_or_reasoning="Source 1"
        )
    ],
    ethical_issues=[
        EthicalObservation(
            issue_type="Bias",
            severity="None",
            description="No issues"
        )
    ]
)

MOCK_OVERSEER_OUTPUT = OverseerOutput(
    thought_process="Mock Overseer Trace: Verified facts.",
    conclusion="Fact check passed.",
    confidence_score=0.95,
    overseer_data=MOCK_OVERSEER_DATA
)

# 2. Panel Agent
MOCK_PANEL_OUTPUT = PanelOutput(
    thought_process="Mock Panel Trace: Synthesized views.",
    conclusion="Consensus reached.",
    confidence_score=0.9,
    metadata=MOCK_METADATA.model_copy(update={"agentti": "PanelAgent", "vaihe": 3}),
    logician_data=MOCK_LOGICIAN_DATA,
    falsifier_data=MOCK_FALSIFIER_DATA,
    causal_analysis=MOCK_CAUSAL_ANALYSIS,
    performativity_analysis=MOCK_PERFORMATIVITY_ANALYSIS,
    overseer_data=MOCK_OVERSEER_DATA
)

# 3. Judge Agent
MOCK_JUDGE_OUTPUT = EvaluationResult(
    thought_process="Mock Judge Trace: Evaluated all dimensions.",
    conclusion="High quality output.",
    confidence_score=0.9,
    matrix_id="matrix_standard_v1",
    timestamp=datetime.now(),
    total_score=4.5,
    final_verdict="Excellent",
    dimensions=[
        DimensionResultItem(
            dimension_id="logic",
            dimension_label="Logic",
            score=5,
            reasoning="Perfect logic"
        )
    ],
    scale_min=1.0,
    scale_max=5.0,
    score_cards=[
         JudgeScoreCard(
            agent_name="MockJudge",
            total_score=4.5,
            max_score=5,
            scale_min=1.0,
            scale_max=5.0,
            verdict="Excellent",
            dimensions=[
                DimensionResultItem(
                    dimension_id="logic",
                    dimension_label="Logic",
                    score=5,
                    reasoning="Perfect logic"
                )
            ]
        )
    ]
)

# 4. Other Agents
MOCK_INTERACTION_OUTPUT = InteractionAnalysis(
    thought_process="Mock Interaction Trace: Analyzed roles.",
    conclusion="Clear roles defined.",
    confidence_score=0.9,
    metadata=MOCK_METADATA.model_copy(update={"agentti": "InteractionAgent"}),
    role_classification="Architect",
    input_quality_score=0.9,
    improvement_suggestions=["Suggestion 1"]
)

MOCK_PROFILER_OUTPUT = ProfilerAnalysis(
    thought_process="Mock Profiler Trace: Analyzed style.",
    conclusion="Consistent tone.",
    confidence_score=0.9,
    metadata=MOCK_METADATA.model_copy(update={"agentti": "ProfilerAgent"}),
    author_intent="Inform",
    cognitive_biases=["Bias 1"],
    emotional_tone="Neutral",
    metrics={"word_count": 100}
)

MOCK_ARCHIVIST_OUTPUT = ArchivistOutput(
    thought_process="Mock Archivist Trace: Searched cases.",
    conclusion="Precedents found.",
    confidence_score=0.95,
    metadata=MOCK_METADATA.model_copy(update={"agentti": "ArchivistAgent"}),
    relevant_cases=[
        ArchiveCase(
            case_id="case-1",
            similarity_score=0.8,
            verdict="Pass",
            summary="Similar case"
        )
    ],
    consistency_analysis="Consistent",
    stare_decisis_adherence=True,
    compliance_analysis="Aligned",
    compliance_score=4.0
)

MOCK_COACH_OUTPUT = CoachingPlan(
    thought_process="Mock Coach Trace: Formulated plan.",
    conclusion="Actionable steps ready.",
    confidence_score=0.9,
    metadata=MOCK_METADATA.model_copy(update={"agentti": "CoachAgent"}),
    actionable_steps=["Step 1"],
    bibliography=[],
    focus_areas=["Area 1"]
)

MOCK_XAI_OUTPUT = XAIOutput(
    thought_process="Mock XAI Trace: Generated report.",
    conclusion="Report complete.",
    metadata=MOCK_METADATA.model_copy(update={"agentti": "XAIReporterAgent"}),
    executive_summary="Summary",
    analysis_strengths="Strengths",
    analysis_weaknesses="Weaknesses",
    analysis_opportunities="Opportunities",
    analysis_recommendations="Recommendations",
    final_verdict="Verdict",
    confidence_score=0.95,
    score_cards=[
        JudgeScoreCard(
            agent_name="Standard Judge",
            total_score=4.5,
            max_score=5,
            scale_min=1.0,
            scale_max=5.0,
            verdict="High Fidelity",
            dimensions=[
                DimensionResultItem(dimension_id="logic", score=4.5, reasoning="Clear logic"),
                DimensionResultItem(dimension_id="ethics", score=4.5, reasoning="Good ethics"),
            ],
        )
    ]
)

MOCK_GUARD_OUTPUT = GuardOutput(
    thought_process="Mock Guard Trace: Checked security.",
    conclusion="Safe to proceed.",
    confidence_score=1.0,
    security_check=SecurityCheck(
        threat_detected=False,
        risk_level=RiskLevel.LOW,
        risk_score=1.0,
        simulation_score=1.0,
        anonymized=True
    ),
    tainted_data=TaintedDataContent(
        chat_history="History",
        product_text="Product",
        reflection_text="Reflection",
        safe_data="Safe"
    )
)


MOCK_REGISTRY: dict[type[Any], Any] = {
    AnalystOutput: MOCK_ANALYST_OUTPUT,
    PanelOutput: MOCK_PANEL_OUTPUT,
    GuardOutput: MOCK_GUARD_OUTPUT,
    InteractionAnalysis: MOCK_INTERACTION_OUTPUT,
    ProfilerAnalysis: MOCK_PROFILER_OUTPUT,
    ArchivistOutput: MOCK_ARCHIVIST_OUTPUT,
    EvaluationResult: MOCK_JUDGE_OUTPUT,
    CoachingPlan: MOCK_COACH_OUTPUT,
    XAIOutput: MOCK_XAI_OUTPUT,

    # Components
    LogicianData: MOCK_LOGICIAN_DATA,
    FalsifierData: MOCK_FALSIFIER_DATA,
    CausalAnalysis: MOCK_CAUSAL_ANALYSIS,
    PerformativityAnalysis: MOCK_PERFORMATIVITY_ANALYSIS,
    OverseerData: MOCK_OVERSEER_DATA,
    # Outputs
    LogicianOutput: MOCK_LOGICIAN_OUTPUT,
    FalsifierOutput: MOCK_FALSIFIER_OUTPUT,
    CausalOutput: MOCK_CAUSAL_OUTPUT,
    PerformativityOutput: MOCK_PERFORMATIVITY_OUTPUT,
    OverseerOutput: MOCK_OVERSEER_OUTPUT,
}

AGENT_CLASS_TO_MOCK_KEY = {
    "GuardAgent": "guard_agent",
    "AnalystAgent": "analyst_agent",
    "InteractionAnalystAgent": "interaction_agent",
    "LogicianAgent": "logician_agent",
    "LogicalFalsifierAgent": "falsifier_agent",
    "CausalAnalystAgent": "causal_agent",
    "PerformativityDetectorAgent": "performativity_agent",
    "FactualOverseerAgent": "fact_checker_agent",
    "ProfilerAgent": "profiler_agent",
    "ArchivistAgent": "archivist_agent",
    "JudgeAgent": "judge_agent",
    "CoachAgent": "coach_agent",
    "XAIReporterAgent": "xai_agent",
    "PanelAgent": "panel_agent",
}

def get_fallback_data(key: str) -> dict[str, Any]:
    if key == "guard_agent":
        return MOCK_GUARD_OUTPUT.model_dump()
    elif key == "analyst_agent":
        return MOCK_ANALYST_OUTPUT.model_dump()
    elif key == "interaction_agent":
        return MOCK_INTERACTION_OUTPUT.model_dump()
    elif key == "logician_agent":
        return MOCK_LOGICIAN_OUTPUT.model_dump()
    elif key == "falsifier_agent":
        return MOCK_FALSIFIER_OUTPUT.model_dump()
    elif key == "causal_agent":
        return MOCK_CAUSAL_OUTPUT.model_dump()
    elif key == "performativity_agent":
        return MOCK_PERFORMATIVITY_OUTPUT.model_dump()
    elif key == "fact_checker_agent":
        return MOCK_OVERSEER_OUTPUT.model_dump()
    elif key == "profiler_agent":
        return MOCK_PROFILER_OUTPUT.model_dump()
    elif key == "archivist_agent":
        return MOCK_ARCHIVIST_OUTPUT.model_dump()
    elif key == "panel_agent":
        return MOCK_PANEL_OUTPUT.model_dump()
    elif key == "judge_agent":
        return MOCK_JUDGE_OUTPUT.model_dump()
    elif key == "coach_agent":
        return MOCK_COACH_OUTPUT.model_dump()
    elif key == "xai_agent":
        return MOCK_XAI_OUTPUT.model_dump()

    return {"message": "Mock data not found for key", "key": key}
