"""Domain Entities and Agent Output Schemas.

This module contains the strict Pydantic models for all agent outputs.
It enforces a `ReasoningTrace` structure and UI labels for frontend rendering.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

# --- 0. BASE LAYER ---


class Metadata(BaseModel):
    """Metadata container for agent outputs."""
    luontiaika: datetime = Field(..., description="Creation timestamp.")
    agentti: str = Field(..., description="Agent name.")
    vaihe: int = Field(default=0, description="Step number.")
    versio: str = Field(default="1.0", description="Schema version.")
    suoritus_ymparisto: str = Field(default="Unknown", description="Environment.")
    audit_logs: list[dict[str, Any]] | None = Field(default=None, description="Audit logs.")

    model_config = ConfigDict(frozen=False, extra="allow")


class ReasoningTrace(BaseModel):
    """Base class for all agent outputs involving reasoning."""

    reasoning_trace: str = Field(
        ...,
        description="Step-by-step thinking process leading to the result.",
        json_schema_extra={"x-ui-label": "Reasoning Process"},
    )
    metadata: Metadata | None = Field(
        default=None,
        description="System metadata.",
        json_schema_extra={"x-ui-label": "Metadata"},
    )
    semanttinen_tarkistussumma: str | None = Field(
        default=None,
        description="Semantic checksum.",
        json_schema_extra={"x-ui-label": "Checksum"},
    )

    model_config = ConfigDict(frozen=True)


class UsageRecord(BaseModel):
    """Immutable record of LLM token usage and cost."""

    id: str = Field(..., description="Unique ID for the usage event.")
    org_id: str = Field(..., description="Organization ID.")
    user_id: str = Field(..., description="User ID.")
    model: str = Field(..., description="Model name.")
    input_tokens: int = Field(..., description="Input token count.")
    output_tokens: int = Field(..., description="Output token count.")
    cost_usd: float = Field(..., description="Cost in USD.")
    timestamp: datetime = Field(..., description="Timestamp of usage.")

    model_config = ConfigDict(frozen=True)


# --- 1. GUARD LAYER ---



class GuardInput(BaseModel):
    """Input schema for the Guard Agent, supporting strict validation."""
    history_text: str = Field(default="")
    product_text: str = Field(default="")
    reflection_text: str | None = Field(default=None)

    @model_validator(mode="after")
    def validate_banned_phrases(self, info: ValidationInfo) -> 'GuardInput':
        """Validates that no banned phrases are present in the input."""
        context = info.context
        if not context or "banned_phrases" not in context:
            return self

        banned_phrases = context["banned_phrases"]
        if not banned_phrases:
            return self

        # Check all string fields
        data_dict = self.model_dump()
        for key, value in data_dict.items():
            if isinstance(value, str):
                for phrase in banned_phrases:
                    if phrase.lower() in value.lower():
                        raise ValueError(f"SECURITY_BANNED_PHRASE_DETECTED: Found '{phrase}' in field '{key}'")
        return self


class TaintedDataContent(BaseModel):
    """Raw input data wrapper."""

    chat_history: str = Field(..., description="Chat history.")
    product_text: str = Field(..., description="Product text.")
    reflection_text: str = Field(..., description="Reflection text.")
    safe_data: str = Field(..., description="Safe data marker.")


class SecurityCheck(BaseModel):
    """Security check results."""

    threat_detected: bool = Field(
        ...,
        description="Threat detected flag.",
        json_schema_extra={"x-ui-label": "Threat Detected"},
    )
    risk_level: Literal["MATALA", "KESKITASO", "KORKEA"] = Field(
        ...,
        description="Risk level.",
        json_schema_extra={"x-ui-label": "Risk Level"},
    )
    simulation_result: Literal[
        "Passiivinen Matkustaja", "Aktiivinen Arkkitehti", "Haitallinen Toimija"
    ] = Field(
        ...,
        description="Simulation result.",
        json_schema_extra={"x-ui-label": "Simulation Result"},
    )
    anonymized: bool = Field(
        ...,
        description="Was anonymization performed?",
        json_schema_extra={"x-ui-label": "Anonymized"},
    )
    pii_findings: list[str] = Field(
        default_factory=list,
        description="PII findings.",
        json_schema_extra={"x-ui-label": "PII Findings"},
    )


class GuardOutput(ReasoningTrace):
    """Output schema for the Guard Agent."""

    security_check: SecurityCheck = Field(
        ...,
        description="Security scan results.",
        json_schema_extra={"x-ui-label": "Security Check"},
    )
    tainted_data: TaintedDataContent = Field(
        ...,
        description="Raw input data (tainted).",
        json_schema_extra={"x-ui-label": "Input Data"},
    )
    model_config = ConfigDict(frozen=True)


# --- 2. ANALYST LAYER ---


class Hypothesis(BaseModel):
    """A single hypothesis formed by the Analyst."""

    id: str = Field(..., description="Hypothesis ID.")
    claim_text: str = Field(
        ...,
        description="The claim text.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    evidence_found: bool = Field(
        ...,
        description="Was evidence found?",
        json_schema_extra={"x-ui-label": "Evidence Found"},
    )
    search_query: str = Field(
        ...,
        description="Search query used.",
        json_schema_extra={"x-ui-label": "Search Query"},
    )
    quotes: list[str] = Field(
        default_factory=list,
        description="Direct quotes found.",
        json_schema_extra={"x-ui-label": "Quotes"},
    )


class AnalystOutput(ReasoningTrace):
    """Output schema for the Analyst Agent."""

    hypotheses: list[Hypothesis] = Field(
        ...,
        description="List of hypotheses.",
        json_schema_extra={"x-ui-label": "Hypotheses"},
    )
    rag_evidence: list[str] = Field(
        default_factory=list,
        description="RAG evidence snippets.",
        json_schema_extra={"x-ui-label": "RAG Evidence"},
    )
    model_config = ConfigDict(frozen=True)


# --- 3. LOGICIAN LAYER ---


class ToulminComponent(BaseModel):
    """Component of the Toulmin Argumentation Model."""

    id: str = Field(
        ...,
        description="Reference ID.",
        json_schema_extra={"x-ui-label": "ID"},
    )
    claim: str = Field(
        ...,
        description="The conclusion.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    data: str = Field(
        ...,
        description="The evidence.",
        json_schema_extra={"x-ui-label": "Data"},
    )
    warrant: str = Field(
        ...,
        description="The logical bridge.",
        json_schema_extra={"x-ui-label": "Warrant"},
    )
    backing: str | None = Field(
        default=None,
        description="Support for the warrant.",
        json_schema_extra={"x-ui-label": "Backing"},
    )
    rebuttal: str | None = Field(
        default=None,
        description="Counter-arguments.",
        json_schema_extra={"x-ui-label": "Rebuttal"},
    )
    qualifier: str | None = Field(
        default=None,
        description="Degree of certainty.",
        json_schema_extra={"x-ui-label": "Qualifier"},
    )


class CognitiveLevel(BaseModel):
    """Assessment of cognitive depth."""

    bloom_level: str = Field(
        ...,
        description="Bloom's Taxonomy Level.",
        json_schema_extra={"x-ui-label": "Bloom Level"},
    )
    strategic_depth: str = Field(
        ...,
        description="Strategic depth analysis.",
        json_schema_extra={"x-ui-label": "Strategic Depth"},
    )


class WaltonScheme(BaseModel):
    """Walton's Argumentation Scheme."""

    identified_scheme: str = Field(
        ...,
        description="Identified Argumentation Scheme.",
        json_schema_extra={"x-ui-label": "Identified Scheme"},
    )
    critical_questions: list[str] = Field(
        ...,
        description="Critical Questions posed.",
        json_schema_extra={"x-ui-label": "Critical Questions"},
    )


class LogicianData(BaseModel):
    """The core data payload of Logician analysis."""

    toulmin_analysis: list[ToulminComponent] = Field(
        ...,
        description="Toulmin analysis breakdown.",
        json_schema_extra={"x-ui-label": "Toulmin Analysis"},
    )
    cognitive_level: CognitiveLevel = Field(
        ...,
        description="Cognitive level assessment.",
        json_schema_extra={"x-ui-label": "Cognitive Level"},
    )
    walton_scheme: WaltonScheme = Field(
        ...,
        description="Argumentation scheme analysis.",
        json_schema_extra={"x-ui-label": "Argumentation Scheme"},
    )
    toulmin_score: float = Field(
        default=0.0,
        ge=0.0,
        le=6.0,
        description="Calculated score based on components.",
        json_schema_extra={"x-ui-label": "Toulmin Score"},
    )


class LogicianOutput(ReasoningTrace):
    """Output schema for the Logician Agent."""

    logician_data: LogicianData = Field(
        ...,
        description="Logic analysis results.",
        json_schema_extra={"x-ui-label": "Logic Analysis"},
    )
    model_config = ConfigDict(frozen=True)


# --- 5. PANEL LAYER (Consolidation) ---


class WaltonStressTest(BaseModel):
    """Stress test using Walton's critical questions."""

    question: str = Field(
        ...,
        description="The critical question asked.",
        json_schema_extra={"x-ui-label": "Question"},
    )
    evidence_held: bool = Field(
        ...,
        description="Did the evidence hold up?",
        json_schema_extra={"x-ui-label": "Result"},
    )
    observation: str = Field(
        ...,
        description="Observation notes.",
        json_schema_extra={"x-ui-label": "Observation"},
    )


class ReasoningFidelity(BaseModel):
    """Audit of the chain of reasoning fidelity."""

    is_post_hoc: bool = Field(
        ...,
        description="True if post-hoc rationalization detected.",
        json_schema_extra={"x-ui-label": "Post-Hoc Rationalization"},
    )
    justification: str = Field(
        ...,
        description="Reasoning.",
        json_schema_extra={"x-ui-label": "Justification"},
    )
    fidelity_score: Literal["KORKEA", "EPÄVARMA", "HEIKKO"] = Field(
        ...,
        description="Fidelity score.",
        json_schema_extra={"x-ui-label": "Fidelity Score"},
    )


class FalsifierData(BaseModel):
    """Output from the Falsifier component."""

    stress_test_findings: list[WaltonStressTest] = Field(
        ...,
        description="Stress test results.",
        json_schema_extra={"x-ui-label": "Stress Test"},
    )
    fidelity_audit: ReasoningFidelity = Field(
        ...,
        description="Fidelity audit.",
        json_schema_extra={"x-ui-label": "Fidelity Audit"},
    )


class FalsifierOutput(ReasoningTrace):
    """Output schema for the Falsifier Agent."""

    falsifier_data: FalsifierData = Field(
        ...,
        description="Falsification audit result.",
        json_schema_extra={"x-ui-label": "Falsification Audit"},
    )
    model_config = ConfigDict(frozen=True)


class CausalAnalysisData(BaseModel):
    """Data from Causal Audit."""

    timeline_valid: bool = Field(
        ...,
        description="Is the timeline valid?",
        json_schema_extra={"x-ui-label": "Timeline Valid"},
    )
    observation: str = Field(
        ...,
        description="General observations.",
        json_schema_extra={"x-ui-label": "Observations"},
    )


class CounterfactualTest(BaseModel):
    """Counterfactual Simulation Test."""

    scenario_a_actual: str = Field(
        ...,
        description="Actual scenario.",
        json_schema_extra={"x-ui-label": "Actual Scenario"},
    )
    scenario_b_simulated: str = Field(
        ...,
        description="Counterfactual simulation.",
        json_schema_extra={"x-ui-label": "Simulation"},
    )
    plausibility_score: str = Field(
        ...,
        description="Plausibility assessment.",
        json_schema_extra={"x-ui-label": "Plausibility"},
    )


class CausalAnalysis(BaseModel):
    """Output from the Causal component."""

    causal_audit: CausalAnalysisData = Field(
        ...,
        description="Causal audit data.",
        json_schema_extra={"x-ui-label": "Causal Audit"},
    )
    counterfactual_test: CounterfactualTest = Field(
        ...,
        description="Counterfactual test.",
        json_schema_extra={"x-ui-label": "Counterfactual Test"},
    )
    abductive_conclusion: Literal["Aito Oivallus", "Post-Hoc Rationalisointi", "Epävarma"] = Field(
        ...,
        description="Abductive conclusion.",
        json_schema_extra={"x-ui-label": "Abductive Conclusion"},
    )


class CausalOutput(ReasoningTrace):
    """Output schema for the Causal Agent."""

    causal_analysis: CausalAnalysis = Field(
        ...,
        description="Causal audit result.",
        json_schema_extra={"x-ui-label": "Causal Audit"},
    )
    model_config = ConfigDict(frozen=True)


class PerformativityHeuristic(BaseModel):
    """Heuristic check for performativity."""

    heuristic_name: str = Field(
        ...,
        description="Heuristic name.",
        json_schema_extra={"x-ui-label": "Heuristic"},
    )
    flag_raised: bool = Field(
        ...,
        description="Flag raised?",
        json_schema_extra={"x-ui-label": "Flag Raised"},
    )
    description: str = Field(
        ...,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )


class PreMortemAnalysis(BaseModel):
    """Pre-Mortem Analysis results."""

    performed: bool = Field(
        ...,
        description="Was Pre-Mortem performed?",
        json_schema_extra={"x-ui-label": "Performed"},
    )
    weak_signals: list[str] = Field(
        ...,
        description="Detected weak signals.",
        json_schema_extra={"x-ui-label": "Weak Signals"},
    )


class PerformativityAnalysis(BaseModel):
    """(Renamed for schema clarity vs Detector) - Output from Performativity component."""

    performativity_heuristics: list[PerformativityHeuristic] = Field(
        ...,
        description="Heuristics check.",
        json_schema_extra={"x-ui-label": "Heuristics"},
    )
    pre_mortem_analysis: PreMortemAnalysis = Field(
        ...,
        description="Pre-Mortem analysis.",
        json_schema_extra={"x-ui-label": "Pre-Mortem"},
    )
    authenticity_assessment: Literal["Orgaaninen", "Performatiivinen", "Epäilyttävä"] = Field(
        ...,
        description="Overall authenticity assessment.",
        json_schema_extra={"x-ui-label": "Authenticity"},
    )


class PerformativityOutput(ReasoningTrace):
    """Output schema for the Performativity/Detector Agent."""

    performativity_analysis: PerformativityAnalysis = Field(
        ...,
        description="Performativity audit result.",
        json_schema_extra={"x-ui-label": "Performativity Audit"},
    )
    model_config = ConfigDict(frozen=True)


class FactCheckRFI(BaseModel):
    """Request for Information (Fact Check)."""

    claim: str = Field(
        ...,
        description="Claim to check.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    verification_result: Literal["Vahvistettu", "Kumottu", "Ei voitu vahvistaa"] = Field(
        ...,
        description="Result.",
        json_schema_extra={"x-ui-label": "Result"},
    )
    source_or_reasoning: str = Field(
        ...,
        description="Source or reasoning.",
        json_schema_extra={"x-ui-label": "Source/Reasoning"},
    )


class EthicalObservation(BaseModel):
    """Ethical Observation."""

    issue_type: Literal["Syrjintä", "Haitallinen sisältö", "Plagiointi", "Ei havaittu"] = Field(
        ...,
        description="Type of issue.",
        json_schema_extra={"x-ui-label": "Issue Type"},
    )
    severity: Literal["Kriittinen", "Varoitus", "N/A"] = Field(
        ...,
        description="Severity.",
        json_schema_extra={"x-ui-label": "Severity"},
    )
    description: str = Field(
        ...,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )


class OverseerData(BaseModel):
    """Output from the Overseer component."""

    fact_checks: list[FactCheckRFI] = Field(
        default_factory=list,
        description="Fact check report.",
        json_schema_extra={"x-ui-label": "Fact Checks"},
    )
    ethical_observations: list[EthicalObservation] = Field(
        default_factory=list,
        description="Ethical audit report.",
        json_schema_extra={"x-ui-label": "Ethical Issues"},
    )


class OverseerOutput(ReasoningTrace):
    """Output schema for the Overseer Agent."""

    overseer_data: OverseerData = Field(
        ...,
        description="Ethics audit result.",
        json_schema_extra={"x-ui-label": "Ethics Audit"},
    )
    model_config = ConfigDict(frozen=True)


class PanelOutput(ReasoningTrace):
    """Consolidated Output schema for the Panel Agent (Parallel Step).

    Aggregates results from Falsifier, Causal, Detector (Performativity), and Overseer.
    """

    logician_data: LogicianData = Field(
        ...,
        description="Logic audit result (from Logician).",
        json_schema_extra={"x-ui-label": "Logic Audit"},
    )
    falsifier_data: FalsifierData = Field(
        ...,
        description="Falsification audit result.",
        json_schema_extra={"x-ui-label": "Falsification Audit"},
    )
    causal_analysis: CausalAnalysis = Field(
        ...,
        description="Causal audit result.",
        json_schema_extra={"x-ui-label": "Causal Audit"},
    )
    performativity_analysis: PerformativityAnalysis = Field(
        ...,
        description="Performativity audit result.",
        json_schema_extra={"x-ui-label": "Performativity Audit"},
    )
    overseer_data: OverseerData = Field(
        ...,
        description="Ethics audit result.",
        json_schema_extra={"x-ui-label": "Ethics Audit"},
    )

    model_config = ConfigDict(frozen=True)


class TextMetrics(BaseModel):
    """Metrics for text analysis."""
    word_count: int = Field(..., description="Total word count.")
    sentence_count: int = Field(..., description="Total sentence count.")
    avg_sentence_length: float = Field(..., description="Average words per sentence.")
    lexical_diversity: float = Field(..., description="Unique words / total words.")
    capitalization_ratio: float = Field(..., description="Uppercase chars / total chars.")

    model_config = ConfigDict(frozen=True)


# --- 7. JUDGE LAYER ---


class DimensionResultItem(BaseModel):
    """Result for a single dimension."""

    dimension_id: str = Field(
        ...,
        description="ID of the dimension (e.g., 'analysis').",
        json_schema_extra={"x-ui-label": "Dimension ID"},
    )
    dimension_label: str = Field(
        default="",
        description="Human-readable label.",
        json_schema_extra={"x-ui-label": "Dimension"},
    )
    score: int | float = Field(
        ...,
        description="Numerical score.",
        json_schema_extra={"x-ui-label": "Score"},
    )
    reasoning: str = Field(
        ...,
        description="Justification for the score.",
        json_schema_extra={"x-ui-label": "Reasoning"},
    )

    model_config = ConfigDict(extra="forbid")


class JudgeScoreCard(BaseModel):
    """Summary of a single judgment step."""

    agent_name: str = Field(
        ...,
        description="Name of the judge (e.g. 'Standard Judge').",
        json_schema_extra={"x-ui-label": "Judge"},
    )
    total_score: float = Field(
        ...,
        description="Total score (0-5).",
        json_schema_extra={"x-ui-label": "Total Score"},
    )
    max_score: int = Field(
        ...,
        description="Max scale.",
        json_schema_extra={"x-ui-label": "Max Score"},
    )
    verdict: str = Field(
        ...,
        description="Short verdict or summary.",
        json_schema_extra={"x-ui-label": "Verdict"},
    )
    dimensions: list[DimensionResultItem] = Field(
        default_factory=list,
        description="Radar chart data.",
        json_schema_extra={"x-ui-label": "Dimensions"},
    )


class JudgeOutput(ReasoningTrace):
    """Output schema for the Judge Agent."""

    score_card: JudgeScoreCard = Field(
        ...,
        description="Final scorecard.",
        json_schema_extra={"x-ui-label": "Scorecard"},
    )
    scale_min: float = Field(
        default=0.0,
        description="Minimum possible score (usually 0 or 1).",
        json_schema_extra={"x-ui-label": "Scale Min"},
    )
    scale_max: float = Field(
        default=5.0,
        description="Maximum possible score (usually 5).",
        json_schema_extra={"x-ui-label": "Scale Max"},
    )

    model_config = ConfigDict(frozen=True)


# --- 8. XAI LAYER ---



class XAIScoreItem(BaseModel):
    """A single score item for the scorecard."""
    label: str = Field(..., description="Label for the score item.")
    score: float = Field(..., description="Score value.")
    reasoning: str | None = Field(default=None, description="Reasoning for the score.")
    weight: float = Field(default=1.0, description="Weight of this item.")

    model_config = ConfigDict(frozen=True)


class XAIOutput(ReasoningTrace):
    """Output schema for the XAI Reporter Agent."""

    executive_summary: str = Field(
        ...,
        description="High-level summary.",
        json_schema_extra={"x-ui-label": "Executive Summary"},
    )
    analysis_strengths: str = Field(
        ...,
        description="Strengths identified.",
        json_schema_extra={"x-ui-label": "Strengths"},
    )
    analysis_weaknesses: str = Field(
        ...,
        description="Weaknesses identified.",
        json_schema_extra={"x-ui-label": "Weaknesses"},
    )
    analysis_opportunities: str = Field(
        ...,
        description="Opportunities identified.",
        json_schema_extra={"x-ui-label": "Opportunities"},
    )
    analysis_recommendations: str = Field(
        ...,
        description="Recommendations.",
        json_schema_extra={"x-ui-label": "Recommendations"},
    )
    final_verdict: str = Field(
        ...,
        description="Final conclusion.",
        json_schema_extra={"x-ui-label": "Verdict"},
    )
    confidence_score: float = Field(
        ...,
        description="Confidence score (0.0-1.0).",
        json_schema_extra={"x-ui-label": "Confidence"},
    )
    xai_report_formatted: str | None = Field(
        default=None,
        description="Markdown formatted report.",
        json_schema_extra={"x-ui-label": "Formatted Report"},
    )
    comparison_data: dict[str, Any] | None = Field(
        default=None,
        description="Structured comparison data.",
        json_schema_extra={"x-ui-label": "Comparison Data"},
    )
    score_cards: list[JudgeScoreCard] = Field(
        default_factory=list,
        description="Aggregated scores from all judges.",
        json_schema_extra={"x-ui-label": "Scorecards"},
    )

    model_config = ConfigDict(frozen=True)


# --- 9. MISSING MODELS & ALIASES (Migration Support) ---

class ReportContext(BaseModel):
    """Context for the Jinja2 report template."""
    summary: str = Field(..., description="Executive summary.")
    critical_findings: list[str] = Field(..., description="Critical findings.")
    pre_mortem_signals: list[str] = Field(..., description="Pre-mortem signals.")
    hitl_required: bool = Field(..., description="HITL required.")
    ethical_issues: list[dict[str, Any]] = Field(..., description="Ethical issues.")
    audit_questions: list[dict[str, Any]] = Field(..., description="Audit questions.")
    uncertainty: dict[str, Any] = Field(..., description="Uncertainty metrics.")
    scores: dict[str, dict[str, Any]] = Field(..., description="Scores (arvosana, perustelu).")
    average_score: float = Field(..., description="Average score.")
    timestamp: str = Field(..., description="Report timestamp.")
    coaching_plan: dict[str, Any] | None = Field(default=None, description="Coaching plan.")
    penalties_applied: list[str] = Field(default_factory=list, description="Penalties applied.")
    score_summary: str | None = Field(default=None, description="Score summary.")
    input_control_ratio: float | None = Field(default=None, description="Input control ratio.")
    structural_warnings: list[str] = Field(default_factory=list, description="Structural warnings.")
    archivist_precedents: Any | None = Field(default=None, description="Archivist precedents.")
    google_search_results: list[dict[str, Any]] = Field(default_factory=list, description="Google search results.")

    model_config = ConfigDict(frozen=False)


class ArchiveCase(BaseModel):
    """A past case retrieved by the Archivist."""
    case_id: str = Field(..., description="ID of the past case.")
    similarity_score: float = Field(..., description="Similarity to current case.")
    verdict: str = Field(..., description="Verdict of the past case.")
    summary: str = Field(..., description="Summary of the past case.")

class ArchivistOutput(ReasoningTrace):
    """Output schema for the Archivist Agent."""
    relevant_cases: list[ArchiveCase] = Field(
        ...,
        description="Relevant past cases.",
        json_schema_extra={"x-ui-label": "Relevant Cases"},
    )
    consistency_analysis: str = Field(
        ...,
        description="Analysis of consistency with precedents.",
        json_schema_extra={"x-ui-label": "Consistency Analysis"},
    )
    stare_decisis_adherence: bool = Field(
        ...,
        description="Whether the decision follows precedent.",
        json_schema_extra={"x-ui-label": "Stare Decisis"},
    )
    model_config = ConfigDict(frozen=True)

class CoachingPlan(ReasoningTrace):
    """Output schema for the Coach Agent."""
    actionable_steps: list[str] = Field(
        ...,
        description="Concrete steps for improvement.",
        json_schema_extra={"x-ui-label": "Actionable Steps"},
    )
    bibliography: list[dict[str, Any]] = Field(
        ...,
        description="Recommended reading.",
        json_schema_extra={"x-ui-label": "References"},
    )
    focus_areas: list[str] = Field(
        ...,
        description="Key areas to focus on.",
        json_schema_extra={"x-ui-label": "Focus Areas"},
    )
    model_config = ConfigDict(frozen=True)

class ProfilerAnalysis(ReasoningTrace):
    """Output schema for the Profiler Agent."""
    author_intent: str = Field(
        ...,
        description="Assessed intent of the author.",
        json_schema_extra={"x-ui-label": "Author Intent"},
    )
    cognitive_biases: list[str] = Field(
        ...,
        description="Detected cognitive biases.",
        json_schema_extra={"x-ui-label": "Cognitive Biases"},
    )
    emotional_tone: str = Field(
        ...,
        description="Emotional tone analysis.",
        json_schema_extra={"x-ui-label": "Emotional Tone"},
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Quantitative text metrics.",
        json_schema_extra={"x-ui-label": "Metrics"},
    )
    model_config = ConfigDict(frozen=True)

class InteractionAnalysis(ReasoningTrace):
    """Output schema for the Interaction Agent."""
    role_classification: Literal["Driver", "Passenger"] = Field(
        ...,
        description="User role classification.",
        json_schema_extra={"x-ui-label": "Role"},
    )
    input_quality_score: float = Field(
        ...,
        description="Quality score of user input.",
        json_schema_extra={"x-ui-label": "Input Quality"},
    )
    improvement_suggestions: list[str] = Field(
        ...,
        description="Suggestions for better prompting.",
        json_schema_extra={"x-ui-label": "Suggestions"},
    )
    model_config = ConfigDict(frozen=True)

class EvaluationCriterion(BaseModel):
    """A single criterion in an evaluation matrix."""
    id: str
    label: str
    description: str
    weight: float = 1.0

class EvaluationMatrixConfig(BaseModel):
    """Configuration for an Evaluation Matrix."""
    id: str
    name: str
    description: str
    criteria: list[EvaluationCriterion]

class Precedent(BaseModel):
    """A past case/execution retrieved by RetrievalAgent."""
    id: str
    date: str
    scores: str
    verdict: str

class ContextData(ReasoningTrace):
    """Output schema for the Retrieval Agent."""
    precedents: str = Field(..., description="Summary text of precedents.")
    precedent_list: list[Precedent] = Field(default_factory=list, description="Structured list of precedents.")
    model_config = ConfigDict(frozen=True)

class EvaluationResult(BaseModel):
    """Generic container for evaluation results."""
    matrix_id: str
    timestamp: datetime
    total_score: float = Field(..., description="Total score.")
    final_verdict: str = Field(..., description="Final verdict.")
    dimensions: list[DimensionResultItem]
    
    # Scale Metadata (Added for XAI/BFF Compatibility)
    scale_min: float = Field(default=0.0, description="Minimum possible score.")
    scale_max: float = Field(default=5.0, description="Maximum possible score.")

    model_config = ConfigDict(populate_by_name=True)

# --- REGISTRY ---

DOMAIN_REGISTRY = {
    "GuardOutput": GuardOutput,
    "AnalystOutput": AnalystOutput,
    "LogicianOutput": LogicianOutput,
    "PanelOutput": PanelOutput,
    "JudgeOutput": JudgeOutput,
    "XAIOutput": XAIOutput,
    "ArchivistOutput": ArchivistOutput,
    "CoachingPlan": CoachingPlan,
    "ProfilerAnalysis": ProfilerAnalysis,
    "InteractionAnalysis": InteractionAnalysis,
    "ContextData": ContextData,
}
