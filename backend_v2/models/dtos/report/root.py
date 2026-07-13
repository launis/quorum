"""Root ReportDataDto enforcing referential integrity."""

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.dtos.report.atoms import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO


class GlobalSynthesisDTO(BaseModel):
    """Data structure for high-level synthesized reports."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    executive_summary: Annotated[str | None, Field(default=None, description="High-level synthesized summary")]
    urgency_level: Annotated[int | None, Field(default=None)]


class ReportDataDto(BaseModel):
    """The absolute SSOT data contract for the Universal DTO Bridge."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    execution_id: str
    workflow_id: Annotated[str, Field(description="For UI correlation")]
    global_metrics: ExecutionMetricsDTO
    global_synthesis: Annotated[
        GlobalSynthesisDTO | None,
        Field(default=None, description="Stores the final synthesized output of the document."),
    ]
    results: Annotated[
        list[AtomResultDTO],
        Field(
            description="SDUI-RULE: Backend must return this list strictly topologically sorted. Frontend does not compute the DAG."
        ),
    ]
    hydrated_references: Annotated[
        dict[str, HydratedAtomDTO], Field(description="O(1) Dictionary: tda_id -> Static text.")
    ]

    @model_validator(mode="after")
    def enforce_referential_integrity(self) -> Self:
        """FAIL-FAST ARCHITECTURE INVARIANT:
        Ensures that every tda_id present in the results list and dependencies
        actually exists in the hydrated_references dictionary.
        """
        ref_keys = set(self.hydrated_references.keys())

        # Declarative Set Logic (declarative_set_logic_mandate)
        used_ids = {res.tda_id for res in self.results}
        dep_ids = {dep for res in self.results for dep in res.depends_on_tda_ids}
        sc_ids = {sc for res in self.results for sc in res.short_circuit_reason_tda_ids}

        all_referenced_ids = used_ids | dep_ids | sc_ids
        missing_keys = all_referenced_ids - ref_keys

        if missing_keys:
            raise ValueError(f"Referential Integrity Error: Missing keys in hydrated_references: {missing_keys}")

        return self
