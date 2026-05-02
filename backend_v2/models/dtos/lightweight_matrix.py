from pydantic import BaseModel, ConfigDict, Field, RootModel

from backend_v2.models.enums import XaiExtensionType


class OutputProfileConfig(BaseModel):
    """Configuration for Output Profile extensions."""

    visible_extensions: list[XaiExtensionType]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class LightweightMatrixOutput(BaseModel):
    """Strict schema for the Lightweight Matrix Output."""

    raw_score: float
    normalized_score: float = Field(ge=0.0, le=100.0)
    level_breakdown: dict[str, dict[str, int]] | None = None
    justification: str
    evaluated_atoms: dict[str, bool]
    extensions: dict[XaiExtensionType, str]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class MicroCotDTO(BaseModel):
    """Strict schema interceptor for dynamic LLM Micro-CoT outputs."""

    step_4_final_score: float | None = None
    waterfall_calculation_log: str | None = None
    true_atoms: int | None = None
    false_atoms: int | None = None
    total_atoms: int | None = None
    level_breakdown: dict[str, dict[str, int]] | None = None

    # Optional dynamic XAI fields
    step_1_evidence_quote: str | None = None
    step_1b_cited_source_id: str | None = None
    step_1c_google_citation: str | None = None
    step_2_falsification: str | None = None
    extension_coaching: str | None = None
    extension_theory_link: str | None = None
    extension_emotional_sentiment: str | None = None
    extension_remediation_steps: str | None = None
    extension_confidence: float | None = None
    extension_missing_context: str | None = None
    extension_risk_flag: bool | None = None
    evaluation_notes: str | None = None
    step_3_logical_friction: str | None = None

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class StrictMatrixPayload(RootModel[MicroCotDTO]):
    """Strict schema adapter enforcing modern Micro-CoT dicts. Legacy bare floats are explicitly banned."""

    pass


class AtomEvaluationItemDTO(BaseModel):
    """Strict schema for individual atom evaluations in the waterfall pipeline."""

    atom_id: str
    step_1_evidence_type: str | None = None
    step_2_quote: str | None = None
    step_3_implicit_justification: str | None = None
    step_4_reasoning: str = ""
    step_5_boolean: bool = False

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
