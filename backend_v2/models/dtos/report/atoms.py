"""Atom level DTOs for the new Flat Adjacency List structure."""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.dtos.report.shared import ErrorDetailsDTO
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType


class HydratedAtomDTO(BaseModel):
    """Static ontology data. Perfectly cacheable.
    Must not contain any dynamic execution-related data.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    sdui_component: Annotated[
        SDUIComponentType,
        Field(description="Server-Driven UI hint for frontend. Ensures frontend performs no reasoning logic."),
    ]
    resolved_claim: Annotated[str, Field(description="Cleaned claim in human language")]
    source_quote: Annotated[
        str | None,
        Field(default=None, description="Verbatim original quote from the document (static forensic evidence)"),
    ]


class ExtractedValueDTO(BaseModel):
    """Extracted quantitative value and unit."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    value: str | float | int | bool
    unit: Annotated[str | None, Field(default=None, description="Unit of measurement, e.g., 'tCO2e' or 'EUR'")]


class AtomResultDTO(BaseModel):
    """Dynamic execution data (DAG node)."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    tda_id: Annotated[str, Field(description="Opaque ID pointing to the hydrated_references dictionary key")]
    status: ExecutionStatus
    extracted_data: Annotated[
        ExtractedValueDTO | None, Field(default=None, description="Quantitative or isolated result")
    ]
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim original quote from the document")]
    contextual_override: Annotated[
        bool, Field(default=False, description="Allows cognitive override without a verbatim quote")
    ]
    evaluation_reasoning: Annotated[
        str | None, Field(default=None, description="Strictly AI cognitive reasoning, no infra errors")
    ]
    error_details: Annotated[
        ErrorDetailsDTO | None, Field(default=None, description="Populated only if status is SYSTEM_ERROR")
    ]

    depends_on_tda_ids: Annotated[list[str], Field(default_factory=list, description="DAG adjacency list")]
    short_circuit_reason_tda_ids: Annotated[list[str], Field(default_factory=list)]

    @model_validator(mode="before")
    @classmethod
    def validate_cognitive_vs_system_state(cls, data: Any) -> Any:
        """Fail-Fast & Graceful Healing: Prevents hallucinations and incomplete data before freeze."""
        if isinstance(data, dict):
            # Null-Hypothesis Override (blind_extraction_null_hypothesis)
            if data.get("contextual_override") is True and data.get("source_quote") is not None:
                # Healing: If LLM hallucinates quote, wipe it securely
                data["source_quote"] = None

            status = data.get("status")
            if status in ("PASSED", "FAILED", ExecutionStatus.PASSED, ExecutionStatus.FAILED):
                if not data.get("evaluation_reasoning"):
                    raise ValueError(f"Reasoning is mandatory for cognitive status {status}")
                if not data.get("contextual_override") and not data.get("source_quote"):
                    raise ValueError("source_quote is mandatory unless contextual_override is True")

            if status in ("SYSTEM_ERROR", ExecutionStatus.SYSTEM_ERROR) and not data.get("error_details"):
                raise ValueError("Error details are mandatory when status is SYSTEM_ERROR")
        return data
