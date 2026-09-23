"""Step Output DTO for execution traces and domain inputs."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.metadata import StepMetadataDTO
from backend_v2.models.dtos.atom_evaluation import ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.lightweight_matrix import (
    LightweightMatrixOutput,
    ScoringResultDTO,
)
from backend_v2.models.dtos.trace import (
    StepTraceMetadataDTO,
    TraceMatrixPayloadDTO,
    TraceScoringPayloadDTO,
)

__all__ = [
    "StepOutputDTO",
    "StepPayloadValue",
]

type StepPayloadValue = (
    TraceMatrixPayloadDTO
    | LightweightMatrixOutput
    | TraceScoringPayloadDTO
    | ScoringResultDTO
    | AtomResultDTO
    | list[AtomResultDTO]
    | ReducedAtomDTO
    | list[ReducedAtomDTO]
    | FlattenedAtom
    | list[FlattenedAtom]
    | HydratedAtomDTO
    | dict[str, HydratedAtomDTO]
    | StepMetadataDTO
    | StepTraceMetadataDTO
    | dict[str, float]
    | dict[str, str]
    | str
    | int
    | float
    | bool
    | list[str]
    | None
)


class StepOutputDTO(V2CoreBase):
    """Strict execution trace payload format."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    step_id: Annotated[str, Field(description="The opaque DAG Step ID.")]
    block_id: Annotated[str, Field(description="The opaque PromptBlock ID.")]
    data_type: Annotated[
        Literal["text", "matrix", "unknown"],
        Field(description="Inferred or explicitly parsed data type (e.g. matrix, text)."),
    ]
    payload: Annotated[
        StepPayloadValue,
        Field(default=None, description="The actual data payload."),
    ] = None
