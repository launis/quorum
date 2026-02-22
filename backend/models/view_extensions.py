"""Extra UI models for specific section types.

This module defines the structured data payloads for enhanced UiSections
such as Evidence Tables, Reference Lists, and Timeline Feeds.
Strictly adhered to Pydantic V2 and SSOT principles.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- 1. Retrieval / Context ---


class EvidenceItem(BaseModel):
    """A single piece of evidence or knowledge item."""

    id: str = Field(..., description="Unique ID of the item.")
    source: str = Field(..., description="Source document or origin.")
    content: str = Field(..., description="Snippet or summary content.")
    score: float | None = Field(default=None, description="Relevance score (0-1).")
    type: Literal["precedent", "regulation", "concept"] = Field(..., description="Type of evidence.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "source", "content")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class EvidenceList(BaseModel):
    """Payload for SECTION_TYPE.EVIDENCE_LIST."""

    items: list[EvidenceItem] = Field(..., description="List of evidence items.")
    total_count: int = Field(..., description="Total number of items.")

    model_config = ConfigDict(frozen=True, strict=True)


# --- 2. Analyst / Hypotheses ---


class AnalystHypothesis(BaseModel):
    """A single hypothesis row for the Analyst Table."""

    id: str
    claim: str
    proven: bool
    evidence_refs: list[str] = Field(default_factory=list, description="IDs of related evidence.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "claim")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class AnalystTable(BaseModel):
    """Payload for SECTION_TYPE.ANALYST_TABLE."""

    hypotheses: list[AnalystHypothesis]
    rag_evidence: list[str] | None = Field(default=None, description="Legacy list of evidence strings (deprecated).")

    model_config = ConfigDict(frozen=True, strict=True)


# --- 3. Logic / Logician ---


class Argument(BaseModel):
    claim: str
    warrant: str
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("claim", "warrant")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class LogicDisplay(BaseModel):
    bloom_label: str
    bloom_score_display: str
    bloom_percent: float | None
    strategic_label: str
    strategic_score_display: str
    strategic_score: float | None
    strategic_percent: float | None
    toulmin_score_display: str
    toulmin_percent: float | None
    arguments: list[Argument]
    quadrant_label_key: str
    position_label: str
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("bloom_label", "strategic_label", "quadrant_label_key", "position_label")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


# --- 4. Falsification / Stress Test ---


class StressFinding(BaseModel):
    question: str
    result_label: str
    observation: str
    color_class: str
    text_class: str
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("question", "result_label", "observation", "color_class", "text_class")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class FidelityAudit(BaseModel):
    fidelity_score_display: str
    fidelity_percent: float | None
    fidelity_label: str
    post_hoc_rationalization_suspected: bool
    reasoning: str
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("fidelity_score_display", "fidelity_label", "reasoning")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class StressDisplay(BaseModel):
    fidelity_audit: FidelityAudit | None
    findings: list[StressFinding]

    model_config = ConfigDict(frozen=True, strict=True)

    model_config = ConfigDict(frozen=True, strict=True)


# --- 5. Causal Analyst ---


class CausalDisplay(BaseModel):
    abductive_score_display: str
    abductive_percent: float | None
    abductive_conclusion: str
    counterfactual_actual: str
    counterfactual_simulated: str
    plausibility_score_display: str
    plausibility_percent: float | None

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator(
        "abductive_score_display",
        "abductive_conclusion",
        "counterfactual_actual",
        "counterfactual_simulated",
        "plausibility_score_display",
    )
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


# --- 6. Performativity / Detector ---


class Heuristic(BaseModel):
    name: str
    icon: str
    color: str
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("name", "icon", "color")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class PerformativityDisplay(BaseModel):
    authenticity_score: float
    authenticity_percent: float | None
    authenticity_assessment: str
    heuristics: list[Heuristic]
    ethical_issues: list[EthicalIssue]
    model_config = ConfigDict(frozen=True, strict=True)


# --- 7. Fact Check / Overseer ---


class VerifiedFact(BaseModel):
    label: str
    claim: str
    source: str
    color: str

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("label", "claim", "source", "color")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class EthicalIssue(BaseModel):
    issue: str
    label: str
    description: str
    color: str

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("issue", "label", "description", "color")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class FactCheckDisplay(BaseModel):
    verified_facts: list[VerifiedFact]
    ethical_issues: list[EthicalIssue]
    model_config = ConfigDict(frozen=True, strict=True)


# --- 8. Profiler / Control Ratio ---


class ProfilerDisplay(BaseModel):
    control_ratio_display: str
    control_ratio_percent: float | None
    control_label: str
    word_count_display: str
    avg_sentence_length_display: str
    lexical_diversity_display: str
    capitalization_ratio_display: str
    automation_bias_label: str
    automation_bias_color: str
    say_do_gap_label: str
    say_do_gap_color: str
    psychological_profile: str
    intent_analysis: str

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator(
        "control_label",
        "automation_bias_label",
        "automation_bias_color",
        "say_do_gap_label",
        "say_do_gap_color",
        "psychological_profile",
        "intent_analysis",
    )
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


# --- 9. Archivist / Compliance ---


class ArchivistDisplay(BaseModel):
    compliance_score: float | None
    compliance_analysis: str
    recommendations: list[str]

    model_config = ConfigDict(frozen=True, strict=True)

    # No fields to validate for non-empty string in ArchivistDisplay currently,
    # or add correct validator if needed.
    # compliance_analysis is str. recommendations is list.
    @field_validator("compliance_analysis")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


# --- 10. Driver Profile / Interaction ---


class DriverDisplay(BaseModel):
    classification: str
    input_quality_label: str
    strategies: list[str]

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("classification", "input_quality_label")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


# --- 11. Security / Guard ---


class SecurityDisplay(BaseModel):
    threat_label: str
    threat_color: str
    risk_label: str
    risk_color: str
    anonymized_label: str
    anonymized_color: str
    findings: list[str]

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("threat_label", "threat_color", "risk_label", "risk_color", "anonymized_label", "anonymized_color")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()
