"""Mock Data Store for AI Layer Testing (Zero-Token Cost)."""

from typing import Any

from backend.models.domain import (
    ArchivistOutput,
    CausalAnalysis,
    CausalAnalysisData,
    CoachingPlan,
    CounterfactualTest,
    DimensionResultItem,
    EthicalObservation,
    EvaluationResult,
    FactCheckRFI,
    FalsifierData,
    Hypoteesi,
    InteractionAnalysis,
    KognitiivinenTaso,
    LogicianData,
    Metadata,
    OverseerData,
    PanelOutput,
    PerformativityAnalysis,
    PerformativityHeuristic,
    PreMortemAnalysis,
    ProfilerAnalysis,
    RagTodiste,
    ReasoningFidelity,
    SafeDataContent,
    JudgeScoreCard,
    SecurityCheck,
    TaintedDataContent,
    AnalystOutput,
    ToulminKomponentti,
    WaltonSkeema,
    WaltonStressTest,
    XAIOutput,
    XAIScoreItem,
)

# ... (omitted lines)

# 9. XAI Report
MOCK_XAI_OUTPUT = XAIOutput(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "XAI", "vaihe": 13}),
    metodologinen_loki="Mock XAI",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_xai",
    executive_summary="[TIIVISTELMÄ]",
    analysis_strengths="[VAHVUUDET]",
    analysis_weaknesses="[HEIKKOUDET]",
    analysis_opportunities="[MAHDOLLISUUDET]",
    analysis_recommendations="[SUOSITUKSET]",
    final_verdict="[LOPPUTULOS]",
    confidence_score=0.95,
    comparison_data={"status": "Mock Comparison Data"},
    score_cards=[
        JudgeScoreCard(
            agent_name="Standard Judge",
            total_score=4.5,
            max_score=5,
            verdict="High Fidelity",
            dimensions=[
                DimensionResultItem(dimension_id="logic", score=4.5, reasoning="Clear logic"),
                DimensionResultItem(dimension_id="ethics", score=4.5, reasoning="Good ethics"),
            ],
        )
    ],
)


# 10. Tainted Data (Guard Agent Model)
MOCK_TAINTED_DATA = TaintedDataContent(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "GuardAgent", "vaihe": 1}),
    metodologinen_loki="Mock Guard Scan",
    edellisen_vaiheen_validointi="N/A",
    semanttinen_tarkistussumma="hash_guard",
    data=TaintedDataContent(
        keskusteluhistoria="{{FILE: Keskusteluhistoria.pdf}}",
        lopputuote="{{FILE: Lopputuote.pdf}}",
        reflektiodokumentti="{{FILE: Reflektiodokumentti.pdf}}",
    ),
    security_check=SecurityCheck(
        uhka_havaittu=False,
        adversariaalinen_simulaatio_tulos="[SIMULAATION TULOS]",
        riski_taso="MATALA",
        anonymisointi_tehty=True,
        tietosuoja_raportti="Mock data redacted.",
    ),
    safe_data=SafeDataContent(
        keskusteluhistoria="Sanitized history",
        lopputuote="Sanitized product",
        reflektiodokumentti="Sanitized reflection",
    ),
)


# Registry Mapping
# Maps the Pydantic MODEL CLASS to the instance
MOCK_REGISTRY: dict[type[Any], Any] = {
    AnalystOutput: MOCK_ANALYST_OUTPUT,
    PanelOutput: MOCK_PANEL_OUTPUT,

    TaintedDataContent: MOCK_TAINTED_DATA,
    InteractionAnalysis: MOCK_INTERACTION_OUTPUT,
    ProfilerAnalysis: MOCK_PROFILER_OUTPUT,
    ArchivistOutput: MOCK_ARCHIVIST_OUTPUT,
    EvaluationResult: MOCK_JUDGE_OUTPUT,
    CoachingPlan: MOCK_COACH_OUTPUT,
    XAIOutput: MOCK_XAI_OUTPUT,
    # Expose Panel Components individually in case tasks are run in isolation
    LogicianData: MOCK_PANEL_OUTPUT.logician_data,
    FalsifierData: MOCK_PANEL_OUTPUT.falsifier_data,
    CausalAnalysis: MOCK_PANEL_OUTPUT.causal_analysis,
    PerformativityAnalysis: MOCK_PANEL_OUTPUT.performativity_analysis,
    OverseerData: MOCK_PANEL_OUTPUT.overseer_data,
}

# --- Lookups & Helpers ---

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
    """Retrieves the default mock data for a given agent key."""
    if key == "guard_agent":
        return MOCK_TAINTED_DATA.model_dump()
    elif key == "analyst_agent":
        return MOCK_ANALYST_OUTPUT.model_dump()
    elif key == "interaction_agent":
        return MOCK_INTERACTION_OUTPUT.model_dump()
    elif key == "logician_agent":
        return MOCK_PANEL_OUTPUT.logician_data.model_dump()
    elif key == "falsifier_agent":
        return MOCK_PANEL_OUTPUT.falsifier_data.model_dump()
    elif key == "causal_agent":
        return MOCK_PANEL_OUTPUT.causal_analysis.model_dump()
    elif key == "performativity_agent":
        return MOCK_PANEL_OUTPUT.performativity_analysis.model_dump()
    elif key == "fact_checker_agent":
        return MOCK_PANEL_OUTPUT.overseer_data.model_dump()
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
