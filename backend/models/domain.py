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


class SecurityCheck(BaseModel):
    """Result of the safety and PII analysis."""

    uhka_havaittu: bool = Field(
        ...,
        description="True if a security threat was detected.",
        json_schema_extra={"x-ui-label": "Threat Detected"},
    )
    riski_taso: Literal["MATALA", "KESKITASO", "KORKEA"] = Field(
        ...,
        description="Assessed risk level.",
        json_schema_extra={"x-ui-label": "Risk Level"},
    )
    adversariaalinen_simulaatio_tulos: str = Field(
        ...,
        description="Explanation of the threat simulation.",
        json_schema_extra={"x-ui-label": "Simulation Result"},
    )
    anonymisointi_tehty: bool = Field(
        default=False,
        description="True if PII redaction was performed.",
        json_schema_extra={"x-ui-label": "PII Redacted"},
    )
    tietosuoja_raportti: str | None = Field(
        default=None,
        description="Report on what PII was removed.",
        json_schema_extra={"x-ui-label": "Privacy Report"},
    )


class TaintedDataContent(BaseModel):
    """Wrapper for file pointers to potential PII-laden content."""

    keskusteluhistoria: str | None = Field(
        default=None,
        description="Pointer to history file.",
        json_schema_extra={"x-ui-label": "History File"},
    )
    lopputuote: str | None = Field(
        default=None,
        description="Pointer to product file.",
        json_schema_extra={"x-ui-label": "Product File"},
    )
    reflektiodokumentti: str | None = Field(
        default=None,
        description="Pointer to reflection file.",
        json_schema_extra={"x-ui-label": "Reflection File"},
    )


class SafeDataContent(BaseModel):
    """Sanitized data content (PII removed)."""

    keskusteluhistoria: str | None = Field(
        default=None,
        description="Sanitized history.",
        json_schema_extra={"x-ui-label": "Sanitized History"},
    )
    lopputuote: str | None = Field(
        default=None,
        description="Sanitized product.",
        json_schema_extra={"x-ui-label": "Sanitized Product"},
    )
    reflektiodokumentti: str | None = Field(
        default=None,
        description="Sanitized reflection.",
        json_schema_extra={"x-ui-label": "Sanitized Reflection"},
    )


class GuardOutput(ReasoningTrace):
    """Output schema for the Guard Agent."""

    security_check: SecurityCheck = Field(
        ...,
        description="Security analysis results.",
        json_schema_extra={"x-ui-label": "Security Check"},
    )
    data: TaintedDataContent = Field(
        ...,
        description="Pointer to source files.",
        json_schema_extra={"x-ui-label": "Source Data"},
    )
    safe_data: Literal["DATA_CHECKED_AND_SECURED"] = Field(
        default="DATA_CHECKED_AND_SECURED",
        description="Confirmation tag.",
        json_schema_extra={"x-ui-label": "Status Tag"},
    )
    sanitized_content: SafeDataContent | None = Field(
        default=None,
        description="Sanitized content payload.",
        json_schema_extra={"x-ui-label": "Sanitized Content"},
    )

    model_config = ConfigDict(frozen=True)


# --- 2. ANALYST LAYER ---


class Hypoteesi(BaseModel):
    """A research hypothesis formulated by the Analyst."""

    id: str = Field(
        ...,
        description="Unique ID for the hypothesis.",
        json_schema_extra={"x-ui-label": "ID"},
    )
    vaite_teksti: str = Field(
        ...,
        description="The hypothesis claim text.",
        json_schema_extra={"x-ui-label": "Hypothesis"},
    )
    loytyyko_todisteita: bool = Field(
        ...,
        description="Whether evidence was found.",
        json_schema_extra={"x-ui-label": "Evidence Found"},
    )
    hakusana_ehdotus: str | None = Field(
        default=None,
        description="Suggested Google search query.",
        json_schema_extra={"x-ui-label": "Search Query"},
    )


class RagTodiste(BaseModel):
    """Evidence retrieved via RAG."""

    viittaa_hypoteesiin_id: str | list[str] = Field(
        ...,
        description="ID(s) of the hypothesis this evidence supports.",
        json_schema_extra={"x-ui-label": "Linked Hypothesis"},
    )
    perusteet: str = Field(
        ...,
        description="Reasoning why this evidence is relevant.",
        json_schema_extra={"x-ui-label": "Relevance Reasoning"},
    )
    konteksti_segmentti: str = Field(
        ...,
        description="The concise text excerpt (quote).",
        json_schema_extra={"x-ui-label": "Quote"},
    )
    relevanssi_score: int = Field(
        ...,
        ge=1,
        le=100,
        description="Relevance score (1-100).",
        json_schema_extra={"x-ui-label": "Relevance Score"},
    )


class AnalystOutput(ReasoningTrace):
    """Output schema for the Analyst Agent."""

    hypoteesit: list[Hypoteesi] = Field(
        ...,
        description="List of formulated hypotheses.",
        json_schema_extra={"x-ui-label": "Hypotheses"},
    )
    rag_todisteet: list[RagTodiste] = Field(
        ...,
        description="Evidence collected from RAG.",
        json_schema_extra={"x-ui-label": "Evidence"},
    )

    model_config = ConfigDict(frozen=True)


# --- 3. LOGICIAN LAYER ---


class ToulminKomponentti(BaseModel):
    """Component of the Toulmin Argumentation Model."""

    vaite_id: str = Field(
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


class KognitiivinenTaso(BaseModel):
    """Assessment of cognitive depth."""

    bloom_taso: str = Field(
        ...,
        description="Bloom's Taxonomy Level.",
        json_schema_extra={"x-ui-label": "Bloom Level"},
    )
    strateginen_syvyys: str = Field(
        ...,
        description="Strategic depth analysis.",
        json_schema_extra={"x-ui-label": "Strategic Depth"},
    )


class WaltonSkeema(BaseModel):
    """Walton's Argumentation Scheme."""

    tunnistettu_skeema: str = Field(
        ...,
        description="Identified Argumentation Scheme.",
        json_schema_extra={"x-ui-label": "Identified Scheme"},
    )
    kriittiset_kysymykset: list[str] = Field(
        ...,
        description="Critical Questions posed.",
        json_schema_extra={"x-ui-label": "Critical Questions"},
    )


class LogicianData(BaseModel):
    """The core data payload of Logician analysis."""

    toulmin_analyysi: list[ToulminKomponentti] = Field(
        ...,
        description="Toulmin analysis breakdown.",
        json_schema_extra={"x-ui-label": "Toulmin Analysis"},
    )
    kognitiivinen_taso: KognitiivinenTaso = Field(
        ...,
        description="Cognitive level assessment.",
        json_schema_extra={"x-ui-label": "Cognitive Level"},
    )
    walton_skeema: WaltonSkeema = Field(
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

    kysymys: str = Field(
        ...,
        description="The critical question asked.",
        json_schema_extra={"x-ui-label": "Question"},
    )
    kestiko_todistusaineisto: bool = Field(
        ...,
        description="Did the evidence hold up?",
        json_schema_extra={"x-ui-label": "Result"},
    )
    havainto: str = Field(
        ...,
        description="Observation notes.",
        json_schema_extra={"x-ui-label": "Observation"},
    )


class ReasoningFidelity(BaseModel):
    """Audit of the chain of reasoning fidelity."""

    onko_post_hoc_rationalisointia: bool = Field(
        ...,
        description="True if post-hoc rationalization detected.",
        json_schema_extra={"x-ui-label": "Post-Hoc Rationalization"},
    )
    perustelu: str = Field(
        ...,
        description="Reasoning.",
        json_schema_extra={"x-ui-label": "Justification"},
    )
    uskollisuus_score: Literal["KORKEA", "EPÄVARMA", "HEIKKO"] = Field(
        ...,
        description="Fidelity score.",
        json_schema_extra={"x-ui-label": "Fidelity Score"},
    )


class FalsifierData(BaseModel):
    """Output from the Falsifier component."""

    walton_stressitesti_loydokset: list[WaltonStressTest] = Field(
        ...,
        description="Stress test results.",
        json_schema_extra={"x-ui-label": "Stress Test"},
    )
    paattelyketjun_uskollisuus_auditointi: ReasoningFidelity = Field(
        ...,
        description="Fidelity audit.",
        json_schema_extra={"x-ui-label": "Fidelity Audit"},
    )


class CausalAnalysisData(BaseModel):
    """Data from Causal Audit."""

    aikajana_validi: bool = Field(
        ...,
        description="Is the timeline valid?",
        json_schema_extra={"x-ui-label": "Timeline Valid"},
    )
    havainto: str = Field(
        ...,
        description="General observations.",
        json_schema_extra={"x-ui-label": "Observations"},
    )


class CounterfactualTest(BaseModel):
    """Counterfactual Simulation Test."""

    skenaario_A_toteutunut: str = Field(
        ...,
        description="Actual scenario.",
        json_schema_extra={"x-ui-label": "Actual Scenario"},
    )
    skenaario_B_simulaatio: str = Field(
        ...,
        description="Counterfactual simulation.",
        json_schema_extra={"x-ui-label": "Simulation"},
    )
    uskottavuus_arvio: str = Field(
        ...,
        description="Plausibility assessment.",
        json_schema_extra={"x-ui-label": "Plausibility"},
    )


class CausalAnalysis(BaseModel):
    """Output from the Causal component."""

    kausaalinen_auditointi: CausalAnalysisData = Field(
        ...,
        description="Causal audit data.",
        json_schema_extra={"x-ui-label": "Causal Audit"},
    )
    kontrafaktuaalinen_testi: CounterfactualTest = Field(
        ...,
        description="Counterfactual test.",
        json_schema_extra={"x-ui-label": "Counterfactual Test"},
    )
    abduktiivinen_paatelma: Literal["Aito Oivallus", "Post-Hoc Rationalisointi", "Epävarma"] = Field(
        ...,
        description="Abductive conclusion.",
        json_schema_extra={"x-ui-label": "Abductive Conclusion"},
    )


class PerformativityHeuristic(BaseModel):
    """Heuristic check for performativity."""

    heuristiikka: str = Field(
        ...,
        description="Heuristic name.",
        json_schema_extra={"x-ui-label": "Heuristic"},
    )
    lippu_nostettu: bool = Field(
        ...,
        description="Flag raised?",
        json_schema_extra={"x-ui-label": "Flag Raised"},
    )
    kuvaus: str = Field(
        ...,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )


class PreMortemAnalysis(BaseModel):
    """Pre-Mortem Analysis results."""

    suoritettu: bool = Field(
        ...,
        description="Was Pre-Mortem performed?",
        json_schema_extra={"x-ui-label": "Performed"},
    )
    hiljaiset_signaalit: list[str] = Field(
        ...,
        description="Detected weak signals.",
        json_schema_extra={"x-ui-label": "Weak Signals"},
    )


class PerformativityAnalysis(BaseModel):
    """(Renamed for schema clarity vs Detector) - Output from Performativity component."""

    performatiivisuus_heuristiikat: list[PerformativityHeuristic] = Field(
        ...,
        description="Heuristics check.",
        json_schema_extra={"x-ui-label": "Heuristics"},
    )
    pre_mortem_analyysi: PreMortemAnalysis = Field(
        ...,
        description="Pre-Mortem analysis.",
        json_schema_extra={"x-ui-label": "Pre-Mortem"},
    )
    yleisarvio_aitoudesta: Literal["Orgaaninen", "Performatiivinen", "Epäilyttävä"] = Field(
        ...,
        description="Overall authenticity assessment.",
        json_schema_extra={"x-ui-label": "Authenticity"},
    )


class FactCheckRFI(BaseModel):
    """Request for Information (Fact Check)."""

    vaite: str = Field(
        ...,
        description="Claim to check.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    verifiointi_tulos: Literal["Vahvistettu", "Kumottu", "Ei voitu vahvistaa"] = Field(
        ...,
        description="Result.",
        json_schema_extra={"x-ui-label": "Result"},
    )
    lahde_tai_paattely: str = Field(
        ...,
        description="Source or reasoning.",
        json_schema_extra={"x-ui-label": "Source/Reasoning"},
    )


class EthicalObservation(BaseModel):
    """Ethical Observation."""

    tyyppi: Literal["Syrjintä", "Haitallinen sisältö", "Plagiointi", "Ei havaittu"] = Field(
        ...,
        description="Type of issue.",
        json_schema_extra={"x-ui-label": "Issue Type"},
    )
    vakavuus: Literal["Kriittinen", "Varoitus", "N/A"] = Field(
        ...,
        description="Severity.",
        json_schema_extra={"x-ui-label": "Severity"},
    )
    kuvaus: str = Field(
        ...,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )


class OverseerData(BaseModel):
    """Output from the Overseer component."""

    faktantarkistus_rfi: list[FactCheckRFI] = Field(
        default_factory=list,
        description="Fact check report.",
        json_schema_extra={"x-ui-label": "Fact Checks"},
    )
    eettiset_havainnot: list[EthicalObservation] = Field(
        default_factory=list,
        description="Ethical audit report.",
        json_schema_extra={"x-ui-label": "Ethical Issues"},
    )


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
    relevant_cases: list[ArchiveCase] = Field(..., description="Relevant past cases.")
    consistency_analysis: str = Field(..., description="Analysis of consistency with precedents.")
    stare_decisis_adherence: bool = Field(..., description="Whether the decision follows precedent.")
    model_config = ConfigDict(frozen=True)

class CoachingPlan(ReasoningTrace):
    """Output schema for the Coach Agent."""
    actionable_steps: list[str] = Field(..., description="Concrete steps for improvement.")
    bibliography: list[dict[str, Any]] = Field(..., description="Recommended reading.")
    focus_areas: list[str] = Field(..., description="Key areas to focus on.")
    model_config = ConfigDict(frozen=True)

class ProfilerAnalysis(ReasoningTrace):
    """Output schema for the Profiler Agent."""
    author_intent: str = Field(..., description="Assessed intent of the author.")
    cognitive_biases: list[str] = Field(..., description="Detected cognitive biases.")
    emotional_tone: str = Field(..., description="Emotional tone analysis.")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Quantitative text metrics.")
    model_config = ConfigDict(frozen=True)

class InteractionAnalysis(ReasoningTrace):
    """Output schema for the Interaction Agent."""
    role_classification: Literal["Driver", "Passenger"] = Field(..., description="User role classification.")
    input_quality_score: float = Field(..., description="Quality score of user input.")
    improvement_suggestions: list[str] = Field(..., description="Suggestions for better prompting.")
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
