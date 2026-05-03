from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    @model_validator(mode="before")
    @classmethod
    def hydrate_extension_keys(cls, data: Any) -> Any:
        """Hydrates JSON string keys into XaiExtensionType instances before strict validation.
        Also acts as the Zero-Legacy boundary, mapping flat LLM Micro-CoT keys into the structured V2 format.
        """
        if not isinstance(data, dict):
            return data

        # Schema map for dynamic XAI Extension extraction
        xai_field_map = {
            "step_1_evidence_quote": XaiExtensionType.CITATION,
            "step_1b_cited_source_id": XaiExtensionType.SOURCE_ID,
            "step_2_falsification": XaiExtensionType.FALSIFICATION,
            "extension_coaching": XaiExtensionType.COACHING,
            "extension_theory_link": XaiExtensionType.THEORY_LINK,
            "extension_emotional_sentiment": XaiExtensionType.EMOTIONAL_SENTIMENT,
            "extension_remediation_steps": XaiExtensionType.REMEDIATION_STEPS,
        }

        # 1. Map flat LLM Micro-CoT keys to V2 structures
        if "step_4_final_score" in data and "raw_score" not in data:
            data["raw_score"] = float(data.pop("step_4_final_score"))

        if "raw_score" not in data:
            data["raw_score"] = 0.0  # Fallback for text-only PromptBlocks

        if "normalized_score" not in data:
            data["normalized_score"] = data["raw_score"]

        just_parts = []
        if "evaluation_notes" in data:
            just_parts.append(str(data.pop("evaluation_notes")))
        if "step_3_logical_friction" in data:
            just_parts.append(str(data.pop("step_3_logical_friction")))

        if just_parts and "justification" not in data:
            data["justification"] = "\n\n".join(just_parts)

        if "justification" not in data:
            data["justification"] = ""

        if "evaluated_atoms" not in data:
            data["evaluated_atoms"] = {}

        if "extensions" not in data:
            data["extensions"] = {}

        # 2. Extract and hydrate XAI extensions from flat keys
        for flat_key, enum_type in xai_field_map.items():
            if flat_key in data:
                data["extensions"][enum_type] = str(data.pop(flat_key))

        # 3. Hydrate any string keys inside the extensions dict (for API JSON parsing)
        exts = data["extensions"]
        if isinstance(exts, dict):
            hydrated: dict[Any, Any] = {}
            for k, v in exts.items():
                if isinstance(k, str):
                    try:
                        hydrated[XaiExtensionType(k)] = v
                    except ValueError:
                        hydrated[k] = v  # Invalid enum value, let strict validation catch it
                else:
                    hydrated[k] = v
            data["extensions"] = hydrated

        return data


class AtomEvaluationItemDTO(BaseModel):
    """Strict schema for individual atom evaluations in the waterfall pipeline."""

    atom_id: str
    step_1_evidence_type: str | None = None
    step_2_quote: str | None = None
    step_3_implicit_justification: str | None = None
    step_4_reasoning: str = ""
    step_5_boolean: bool = False

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
