"""Domain Entities and Agent Output Schemas.

This module contains the strict Pydantic models for all agent outputs.
It enforces a `ReasoningTrace` structure and UI labels for frontend rendering.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

# --- 0. BASE LAYER ---


# --- L10N LOOKUP (Backend-Driven Helper) ---
from backend.services.localization import LocalizationService


def _map_l10n_values(definitions: list[tuple[str, float]]) -> dict[str, float]:
    """Helper to build reverse mapping from localized strings to numeric values."""
    mapping = {}
    for key, val in definitions:
        # Check EN, FI, and current context for robustness
        mapping[LocalizationService.translate(key, "en")] = val
        mapping[LocalizationService.translate(key, "fi")] = val
        mapping[LocalizationService.translate(key)] = val
    return mapping


def _map_l10n_boolean(definitions: list[tuple[str, bool]]) -> dict[str, bool]:
    """Helper to build reverse mapping from localized strings to boolean values."""
    mapping = {}
    for key, val in definitions:
        mapping[LocalizationService.translate(key, "en")] = val
        mapping[LocalizationService.translate(key, "fi")] = val
        mapping[LocalizationService.translate(key)] = val
    return mapping

# --- L10N LOOKUP (Backend-Driven Helper) ---
# DEPRECATED: Now using LocalizationService
# L10N_LOOKUP = { ... }


class Metadata(BaseModel):
    """Metadata container for agent outputs."""
    luontiaika: datetime = Field(..., description="Creation timestamp.", json_schema_extra={"x-ui-label": "Creation Time"})
    agentti: str = Field(..., description="Agent name.", json_schema_extra={"x-ui-label": "Agent Name"})
    vaihe: int = Field(default=0, description="Step number.", json_schema_extra={"x-ui-label": "Step Number"})
    versio: str = Field(default="1.0", description="Schema version.", json_schema_extra={"x-ui-label": "Version"})
    suoritus_ymparisto: str = Field(default="Unknown", description="Environment.", json_schema_extra={"x-ui-label": "Environment"})
    audit_logs: list[dict[str, Any]] | None = Field(default=None, description="Audit logs.", json_schema_extra={"x-ui-label": "Audit Logs"})

    @field_validator('luontiaika', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

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

    id: str = Field(..., description="Unique ID for the usage event.", json_schema_extra={"x-ui-label": "ID"})
    org_id: str = Field(..., description="Organization ID.", json_schema_extra={"x-ui-label": "Organization ID"})
    user_id: str = Field(..., description="User ID.", json_schema_extra={"x-ui-label": "User ID"})
    model: str = Field(..., description="Model name.", json_schema_extra={"x-ui-label": "Model"})
    input_tokens: int = Field(..., description="Input token count.", json_schema_extra={"x-ui-label": "Input Tokens"})
    output_tokens: int = Field(..., description="Output token count.", json_schema_extra={"x-ui-label": "Output Tokens"})
    cost_usd: float = Field(..., description="Cost in USD.", json_schema_extra={"x-ui-label": "Cost (USD)"})
    timestamp: datetime = Field(..., description="Timestamp of usage.", json_schema_extra={"x-ui-label": "Timestamp"})

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Fallback for ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    model_config = ConfigDict(frozen=True)

class GuardInput(BaseModel):
    """Input schema for the Guard Agent, supporting strict validation."""
    history_text: str = Field(..., json_schema_extra={"x-ui-label": "INPUT_HISTORY_TEXT"})
    product_text: str = Field(..., json_schema_extra={"x-ui-label": "INPUT_PRODUCT_TEXT"})
    reflection_text: str | None = Field(default=None, json_schema_extra={"x-ui-label": "INPUT_REFLECTION_TEXT"})

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

    chat_history: str = Field(..., description="Chat history.", json_schema_extra={"x-ui-label": "INPUT_CHAT_HISTORY"})
    product_text: str = Field(..., description="Product text.", json_schema_extra={"x-ui-label": "INPUT_PRODUCT_TEXT"})
    reflection_text: str = Field(..., description="Reflection text.", json_schema_extra={"x-ui-label": "INPUT_REFLECTION_TEXT"})
    safe_data: str = Field(..., description="Safe data marker.", json_schema_extra={"x-ui-label": "INPUT_SAFE_DATA"})


class SecurityCheck(BaseModel):
    """Security check results."""

    threat_detected: bool = Field(
        ...,
        description="Threat detected flag.",
        json_schema_extra={"x-ui-label": "Threat Detected"},
    )
    risk_level: str = Field(
        ...,
        description="Risk level.",
        json_schema_extra={"x-ui-label": "Risk Level"},
    )
    risk_score: float = Field(
        ...,
        description="Numeric Risk score (1-3).",
        json_schema_extra={"x-ui-label": "Risk Score"},
    )
    simulation_score: float = Field(
        ...,
        description="Numeric Simulation score (1-3).",
        json_schema_extra={"x-ui-label": "Simulation Score"},
    )

    @model_validator(mode="before")
    @classmethod
    def calc_scores(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Calc Risk
            mapping_risk = _map_l10n_values([
                ("Risk.Low", 1.0),
                ("Risk.Medium", 2.0),
                ("Risk.High", 3.0)
            ])
            
            risk_score = data.get("risk_score")
            risk_level = data.get("risk_level")
            
            # Only calculate if not present
            if risk_score is None and risk_level:
                for k, v in mapping_risk.items():
                    if k.lower() in risk_level.lower():
                        data["risk_score"] = v
                        break
            
            # 2. Calc Simulation
            mapping_sim = _map_l10n_values([
                ("Simulation.Passive", 1.0),
                ("Simulation.Active", 2.0),
                ("Simulation.Malicious", 3.0)
            ])
            
            sim_score = data.get("simulation_score")
            sim_res = data.get("simulation_result")

            # Only calculate if not present
            if sim_score is None and sim_res:
                for k, v in mapping_sim.items():
                    if k.lower() in sim_res.lower():
                        data["simulation_score"] = v
                        break

        return data
    
    simulation_result: str | None = Field(
         default=None,
         description="Simulation result description.",
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
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    bloom_score: float = Field(
        ...,
        description="Numeric Bloom score (1-6).",
        json_schema_extra={"x-ui-label": "Bloom Score"},
    )
    strategic_score: float = Field(
        ...,
        description="Numeric Strategic score (1-4).",
        json_schema_extra={"x-ui-label": "Strategic Score"},
    )
    description_key: str = Field(
        default="bloom_desc",
        description="Localization key for help text.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    @model_validator(mode="before")
    @classmethod
    def calculate_scores(cls, data: Any) -> Any:
        """Calculate numeric scores and populate descriptions."""
        if isinstance(data, dict):
            # Populate Description (Context-Aware)
            key = data.get("description_key", "bloom_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)

            # Bloom Mapping (Dynamic L10n)
            bloom_map = _map_l10n_values([
                ("Bloom.Remembering", 1.0), ("Bloom.Understanding", 2.0),
                ("Bloom.Applying", 3.0), ("Bloom.Analyzing", 4.0),
                ("Bloom.Evaluating", 5.0), ("Bloom.Creating", 6.0)
            ])

            bloom_level = data.get("bloom_level")
            current_bloom_score = data.get("bloom_score")
            
            if current_bloom_score is None and bloom_level:
                # Simple fuzzy match or exact match
                for k, v in bloom_map.items():
                    if k.lower() in bloom_level.lower():
                        data["bloom_score"] = v
                        break
            
            # Strategic Mapping (Dynamic L10n)
            strat_map = _map_l10n_values([
                ("Strategic.Low", 1.0), ("Strategic.Medium", 2.0),
                ("Strategic.High", 3.0), ("Strategic.Visionary", 4.0)
            ])

            strategic_depth = data.get("strategic_depth")
            current_strat_score = data.get("strategic_score")

            if current_strat_score is None and strategic_depth:
                 for k, v in strat_map.items():
                    if k.lower() in strategic_depth.lower():
                        data["strategic_score"] = v
                        break
        
        return data
    
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
        ...,
        ge=0.0,
        le=6.0,
        description="Calculated score based on components.",
        json_schema_extra={"x-ui-label": "Toulmin Score"},
    )
    description_key: str = Field(
        default="toulmin_desc",
        description="Localization key for help text.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    @model_validator(mode="before")
    @classmethod
    def pop_desc(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "toulmin_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)
        return data
    
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    fidelity_score: Literal["Weak", "Uncertain", "High"] = Field(
        ...,
        description="Fidelity score.",
        json_schema_extra={"x-ui-label": "Fidelity Score"},
    )
    fidelity_numeric: float = Field(
        ...,
        description="Numeric Fidelity score (1-3).",
    )
    description_key: str = Field(
        default="fidelity_desc",
        description="Localization key.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    @model_validator(mode="before")
    @classmethod
    def calc_fidelity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "fidelity_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)
                
            mapping = {
                "Weak": 1.0, 
                "Uncertain": 2.0, 
                "High": 3.0
            }
            
            val = data.get("fidelity_score")
            # Only calculate if not provided
            if data.get("fidelity_numeric") is None:
                if val not in mapping:
                    # STRICT VALIDATION: No fallback allowed.
                    raise ValueError(f"Invalid fidelity_score: {val}. Must be one of {list(mapping.keys())}")
                data["fidelity_numeric"] = mapping[val]
        return data

    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    plausibility_score: Literal["Impossible", "Plausible", "High"] = Field(
        ...,
        description="Plausibility assessment.",
        json_schema_extra={"x-ui-label": "Plausibility"},
    )
    plausibility_numeric: float = Field(
        ...,
        description="Numeric Plausibility score (1-3).",
    )
    description_key: str = Field(
        default="plausibility_desc",
        description="Localization key.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    @model_validator(mode="before")
    @classmethod
    def calc_plausibility(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "plausibility_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)
                
            mapping = {
                "Impossible": 1.0,
                "Plausible": 2.0,
                "High": 3.0
            }
                
            val = data.get("plausibility_score")
            # Only calc if numeric missing
            if data.get("plausibility_numeric") is None:
                if val not in mapping:
                    # STRICT VALIDATION: No fallback allowed.
                    raise ValueError(f"Invalid plausibility_score: {val}. Must be one of {list(mapping.keys())}")
                data["plausibility_numeric"] = mapping[val]
        return data

    model_config = ConfigDict(frozen=True)


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
    abductive_conclusion: Literal["Post-Hoc Rationalization", "Uncertain", "Genuine Insight"] = Field(
        ...,
        description="Abductive conclusion.",
        json_schema_extra={"x-ui-label": "Abductive Conclusion"},
    )
    abductive_score: float = Field(
        ...,
        description="Numeric Abductive score (1-3).",
    )
    description_key: str = Field(
        default="abductive_desc",
        description="Localization key.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    @model_validator(mode="before")
    @classmethod
    def calc_abductive(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "abductive_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)
                
            mapping = {
                "Post-Hoc Rationalization": 1.0,
                "Uncertain": 2.0,
                "Genuine Insight": 3.0
            }
                
            val = data.get("abductive_conclusion")
            # Only calc if numeric missing
            if data.get("abductive_score") is None:
                if val not in mapping:
                    # STRICT VALIDATION: No fallback allowed.
                    raise ValueError(f"Invalid abductive_conclusion: {val}. Must be one of {list(mapping.keys())}")
                data["abductive_score"] = mapping[val]
        return data

    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    authenticity_assessment: Literal["Suspicious", "Performative", "Organic"] = Field(
        ...,
        description="Overall authenticity assessment.",
        json_schema_extra={"x-ui-label": "Authenticity"},
    )
    authenticity_score: float = Field(
        ...,
        description="Numeric Authenticity score (1-3).",
    )
    description_key: str = Field(
        default="authenticity_desc",
        description="Localization key.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    @model_validator(mode="before")
    @classmethod
    def calc_authenticity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "authenticity_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)
                
            mapping = {
                "Suspicious": 1.0,
                "Performative": 2.0,
                "Organic": 3.0
            }
                
            val = data.get("authenticity_assessment")
            # Only calc if numeric missing
            if data.get("authenticity_score") is None:
                if val not in mapping:
                    # STRICT VALIDATION: No fallback allowed.
                    raise ValueError(f"Invalid authenticity_assessment: {val}. Must be one of {list(mapping.keys())}")
                data["authenticity_score"] = mapping[val]
        return data

    model_config = ConfigDict(frozen=True)



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
    verification_result: Literal["Verified", "Debunked", "Unverified"] = Field(
        ...,
        description="Result.",
        json_schema_extra={"x-ui-label": "Result"},
    )
    is_verified: bool = Field(
        default=False,
        description="Boolean verification status.",
    )
    source_or_reasoning: str = Field(
        ...,
        description="Source or reasoning.",
        json_schema_extra={"x-ui-label": "Source/Reasoning"},
    )

    @model_validator(mode="before")
    @classmethod
    def calc_verification(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Derive boolean from Literal
            val = data.get("verification_result")
            data["is_verified"] = val == "Verified"
        return data

    model_config = ConfigDict(frozen=True)


class EthicalObservation(BaseModel):
    """Ethical Observation."""

    issue_type: str = Field(
        ...,
        description="Type of ethical issue.",
        json_schema_extra={"x-ui-label": "Issue Type"},
    )
    severity: Literal["None", "Warning", "Critical"] = Field(
        ...,
        description="Severity level.",
        json_schema_extra={"x-ui-label": "Severity"},
    )
    is_critical: bool = Field(
        default=False,
        description="Is the issue critical?",
    )
    description: str = Field(
        ...,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )

    @model_validator(mode="before")
    @classmethod
    def calc_ethics(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Strictly derive booleans from Literal
            val = data.get("severity")
            data["is_critical"] = val == "Critical"
        return data

    model_config = ConfigDict(frozen=True)


class OverseerData(BaseModel):
    """Output from the Overseer component."""

    fact_checks: list[FactCheckRFI] = Field(
        default_factory=list,
        description="Fact check report.",
        json_schema_extra={"x-ui-label": "Fact Checks"},
    )
    ethical_issues: list[EthicalObservation] = Field(
        ...,
        description="Ethical audit report.",
        json_schema_extra={"x-ui-label": "Ethical Issues"},
    )
    model_config = ConfigDict(frozen=True)


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
    word_count: int = Field(..., description="Total word count.", json_schema_extra={"x-ui-label": "Word Count"})
    sentence_count: int = Field(..., description="Total sentence count.", json_schema_extra={"x-ui-label": "Sentence Count"})
    avg_sentence_length: float = Field(..., description="Average words per sentence.", json_schema_extra={"x-ui-label": "Avg Sentence Length"})
    lexical_diversity: float = Field(..., description="Unique words / total words.", json_schema_extra={"x-ui-label": "Lexical Diversity"})
    capitalization_ratio: float = Field(..., description="Uppercase chars / total chars.", json_schema_extra={"x-ui-label": "Capitalization Ratio"})

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
    scale_min: float = Field(
        default=0.0,
        description="Minimum possible score.",
        json_schema_extra={"x-ui-label": "Scale Min"},
    )
    scale_max: float = Field(
        default=5.0,
        description="Maximum possible score.",
        json_schema_extra={"x-ui-label": "Scale Max"},
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
    word_count: int | None = Field(default=None, description="Total word count.")
    structural_warnings: list[str] = Field(default_factory=list, description="Structural warnings.")
    archivist_precedents: Any | None = Field(default=None, description="Archivist precedents.")
    google_search_results: list[dict[str, Any]] = Field(default_factory=list, description="Google search results.")
    
    # Specialist Agents (Deep Analysis)
    logician_data: LogicianData | None = Field(default=None, description="Logician analysis.")
    falsifier_data: FalsifierData | None = Field(default=None, description="Falsifier analysis.")
    causal_analysis: CausalAnalysis | None = Field(default=None, description="Causal analysis.")
    performativity_analysis: PerformativityAnalysis | None = Field(default=None, description="Performativity analysis.")
    overseer_data: OverseerData | None = Field(default=None, description="Overseer analysis.")

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
    compliance_analysis: Literal["Critically Misaligned", "Misaligned", "Neutral", "Aligned", "Strongly Aligned"] = Field(
        ...,
        description="Analysis of consistency with goals (Compliance).",
        json_schema_extra={"x-ui-label": "Compliance Analysis"},
    )
    compliance_score: float = Field(
        default=0.0,
        description="Numeric Compliance score (1-5).",
        json_schema_extra={"x-ui-label": "Compliance Score"},
    )
    description_key: str = Field(
        default="compliance_desc",
        description="Localization key.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    # Deprecated fields kept for backward compatibility if needed, else remove?
    # User asked for everything to work the "same way".
    # Other models use `description`. Archivist used `description_fi`/`description_en`.
    # Let's standardize to `description` and remove the specific language fields to be 100% consistent.

    @model_validator(mode="before")
    @classmethod
    def calc_compliance(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Localization
            # Use 'compliance_desc' as default key if not present, but usually schema defines default.
            # Here we access data dict directly.
            key = data.get("description_key", "compliance_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)

            # 2. Map Literal to Score
            mapping = {
                "Critically Misaligned": 1.0,
                "Misaligned": 2.0,
                "Neutral": 3.0,
                "Aligned": 4.0,
                "Strongly Aligned": 5.0
            }
            
            # Access the raw string value
            val = data.get("compliance_analysis")
            if val not in mapping:
                # STRICT VALIDATION: No fallback allowed.
                raise ValueError(f"Invalid compliance_analysis: {val}. Must be one of {list(mapping.keys())}")
            data["compliance_score"] = mapping[val]
            
        return data
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
    role_classification: Literal["Passenger", "Navigator", "Driver", "Architect"] = Field(
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

    # Container for aggregated results (if applicable)
    score_cards: list[JudgeScoreCard] | None = Field(
        default=None,
        description="List of score cards if this result aggregates multiple."
    )

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Fallback for ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    model_config = ConfigDict(populate_by_name=True)

# --- REGISTRY ---

# --- 10. HOOK RESULT MODELS (Standardized) ---

class SanitizationResult(BaseModel):
    """Result of the text sanitization process (Security Hook)."""
    sanitized_inputs: dict[str, str] = Field(
        ..., 
        description="Sanitized input text fields.", 
        json_schema_extra={"x-ui-label": "Sanitized Inputs"}
    )
    pii_threats_detected: list[str] = Field(
        default_factory=list, 
        description="List of detected PII threats.", 
        json_schema_extra={"x-ui-label": "PII Threats"}
    )
    banned_phrases_detected: list[str] = Field(
        default_factory=list, 
        description="List of detected banned phrases.", 
        json_schema_extra={"x-ui-label": "Banned Phrases"}
    )
    banned_phrases_error: str | None = Field(
        default=None,
        description="Error message if banned phrases fetch failed.",
        json_schema_extra={"x-ui-label": "Banned Phrases Error"}
    )
    
    model_config = ConfigDict(frozen=True)


class PerformativePattern(BaseModel):
    """A single detected performative pattern."""
    pattern_id: str = Field(..., description="ID of the pattern.", json_schema_extra={"x-ui-label": "Pattern ID"})
    detected_phrase: str = Field(..., description="The exact phrase detected.", json_schema_extra={"x-ui-label": "Detected Phrase"})
    category: str = Field(..., description="Category of the pattern.", json_schema_extra={"x-ui-label": "Category"})
    
    model_config = ConfigDict(frozen=True)


class LinguisticsResult(BaseModel):
    """Result of the linguistics analysis (Hook)."""
    performative_patterns: list[PerformativePattern] = Field(
        default_factory=list, 
        description="Detected patterns.", 
        json_schema_extra={"x-ui-label": "Performative Patterns"}
    )
    
    model_config = ConfigDict(frozen=True)


class BibliographyItem(BaseModel):
    """A single bibliographic reference."""
    source_id: str = Field(..., description="Unique source ID.", json_schema_extra={"x-ui-label": "Source ID"})
    title: str = Field(..., description="Title of the source.", json_schema_extra={"x-ui-label": "Title"})
    url: str | None = Field(default=None, description="URL if available.", json_schema_extra={"x-ui-label": "URL"})
    snippet: str | None = Field(default=None, description="Relevant snippet.", json_schema_extra={"x-ui-label": "Snippet"})
    
    model_config = ConfigDict(frozen=True)


class BibliographyResult(BaseModel):
    """Result of the bibliography generation (Hook)."""
    references: list[BibliographyItem] = Field(
        default_factory=list, 
        description="List of references.", 
        json_schema_extra={"x-ui-label": "References"}
    )
    
    model_config = ConfigDict(frozen=True)


class ScoringResult(BaseModel):
    """Result of the scoring logic (Hook)."""
    total_score: float = Field(..., description="Total aggregated score.", json_schema_extra={"x-ui-label": "Total Score"})
    calculated_average: float = Field(..., description="Calculated average.", json_schema_extra={"x-ui-label": "Average Score"})
    score_summary: str = Field(..., description="Summary text.", json_schema_extra={"x-ui-label": "Summary"})
    penalties_applied: list[str] = Field(
        default_factory=list, 
        description="List of penalties applied.", 
        json_schema_extra={"x-ui-label": "Penalties"}
    )
    
    model_config = ConfigDict(frozen=True)


class ReportResult(BaseModel):
    """Result of the report generation (Hook)."""
    report_content: str = Field(..., description="The generated Markdown report.", json_schema_extra={"x-ui-label": "Report Content"})
    format: str = Field(default="markdown", description="Report format.", json_schema_extra={"x-ui-label": "Format"})
    
    model_config = ConfigDict(frozen=True)


class ValidationResult(BaseModel):
    """Result of the structure verification (Hook)."""
    is_valid: bool = Field(..., description="Is the structure valid?", json_schema_extra={"x-ui-label": "Is Valid"})
    errors: list[str] = Field(
        default_factory=list, 
        description="Validation errors.", 
        json_schema_extra={"x-ui-label": "Errors"}
    )
    
    model_config = ConfigDict(frozen=True)


class SearchResultItem(BaseModel):
    """Single search result."""
    title: str = Field(..., description="Title of the result.", json_schema_extra={"x-ui-label": "Title"})
    link: str = Field(..., description="Link to the result.", json_schema_extra={"x-ui-label": "Link"})
    snippet: str = Field(..., description="Snippet of the result.", json_schema_extra={"x-ui-label": "Snippet"})
    
    model_config = ConfigDict(frozen=True)


class SearchResult(BaseModel):
    """Result of the Google Search (Hook)."""
    results: list[SearchResultItem] = Field(
        default_factory=list, 
        description="Search results.", 
        json_schema_extra={"x-ui-label": "Search Results"}
    )
    error: str | None = Field(default=None, description="Error message if search failed.", json_schema_extra={"x-ui-label": "Error"})
    
    model_config = ConfigDict(frozen=True)


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
    # Hook Results
    "SanitizationResult": SanitizationResult,
    "LinguisticsResult": LinguisticsResult,
    "BibliographyResult": BibliographyResult,
    "TextMetrics": TextMetrics,
    "ScoringResult": ScoringResult,
    "ReportResult": ReportResult,
    "ValidationResult": ValidationResult,
    "SearchResult": SearchResult,
}
