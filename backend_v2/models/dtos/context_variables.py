"""Context variables DTO for orchestrator execution and dynamic blackboard sharing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Self

from pydantic import AliasChoices, ConfigDict, Field, TypeAdapter

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput

__all__ = ["ContextVariablesDTO"]


class ContextVariablesDTO(V2CoreBase):
    """Encapsulates execution-level context variables and dynamic blackboard state."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    global_atom_blackboard: Annotated[
        GlobalAtomBlackboard | None,
        Field(
            default=None,
            validation_alias=AliasChoices("global_atom_blackboard", "__GLOBAL_ATOM_BLACKBOARD__"),
            description="Global atom blackboard output",
        ),
    ] = None
    matrix_reducer_output: Annotated[
        LightweightMatrixDTO | LightweightMatrixOutput | None,
        Field(
            default=None,
            validation_alias=AliasChoices("matrix_reducer_output", "__MATRIX_REDUCER_OUTPUT__"),
            description="Matrix reducer output payload",
        ),
    ] = None
    report_context: Annotated[
        DomainInputValue | None,
        Field(default=None, description="Report generation context"),
    ] = None
    step_detector: Annotated[
        DomainInputValue | None,
        Field(default=None, description="Step detector output"),
    ] = None
    evaluated_matrices: Annotated[
        DomainInputValue | None,
        Field(default=None, description="Evaluated matrices summary"),
    ] = None
    variables: Annotated[
        dict[str, DomainInputValue],
        Field(default_factory=dict, description="Typed arbitrary context variables"),
    ] = Field(default_factory=dict)

    def with_update(
        self,
        **updates: DomainInputValue | GlobalAtomBlackboard | LightweightMatrixDTO | LightweightMatrixOutput,
    ) -> Self:
        """Return a new immutable instance with updated fields or dynamic blackboard variables."""
        known_fields = {
            "global_atom_blackboard",
            "matrix_reducer_output",
            "report_context",
            "step_detector",
            "evaluated_matrices",
            "variables",
        }
        field_updates: dict[str, object] = {}
        var_updates: dict[str, DomainInputValue] = dict(self.variables)
        for k, v in updates.items():
            if k == "__GLOBAL_ATOM_BLACKBOARD__":
                field_updates["global_atom_blackboard"] = v
            elif k == "__MATRIX_REDUCER_OUTPUT__":
                field_updates["matrix_reducer_output"] = v
            elif k in known_fields:
                field_updates[k] = v
            elif not isinstance(v, (GlobalAtomBlackboard, LightweightMatrixDTO)):
                var_updates[k] = v
        field_updates["variables"] = var_updates
        return self.model_copy(update=field_updates)

    def to_dict(self) -> dict[str, object]:
        """Convert to flat dictionary for database serialization boundary."""
        res: dict[str, object] = dict(self.variables)
        if self.global_atom_blackboard is not None:
            res["__GLOBAL_ATOM_BLACKBOARD__"] = self.global_atom_blackboard
        if self.matrix_reducer_output is not None:
            res["__MATRIX_REDUCER_OUTPUT__"] = self.matrix_reducer_output
        if self.report_context is not None:
            res["report_context"] = self.report_context
        if self.step_detector is not None:
            res["step_detector"] = self.step_detector
        if self.evaluated_matrices is not None:
            res["evaluated_matrices"] = self.evaluated_matrices
        return res

    @classmethod
    def from_dict(cls, data: Mapping[str, DomainInputValue] | None) -> Self:
        """Hydrate ContextVariablesDTO from a dictionary."""
        if not data:
            return cls()
        global_atom_blackboard: GlobalAtomBlackboard | None = None
        matrix_reducer_output: LightweightMatrixDTO | LightweightMatrixOutput | None = None
        report_context: DomainInputValue | None = None
        step_detector: DomainInputValue | None = None
        evaluated_matrices: DomainInputValue | None = None
        variables: dict[str, DomainInputValue] = {}

        if "variables" in data and isinstance(data["variables"], Mapping):
            for vk, vv in data["variables"].items():
                variables[str(vk)] = vv

        for k, v in data.items():
            if k == "variables":
                continue
            if k in ("__GLOBAL_ATOM_BLACKBOARD__", "global_atom_blackboard"):
                if isinstance(v, GlobalAtomBlackboard) or v is None:
                    global_atom_blackboard = v
                elif isinstance(v, Mapping):
                    global_atom_blackboard = GlobalAtomBlackboard.model_validate(v)
            elif k in ("__MATRIX_REDUCER_OUTPUT__", "matrix_reducer_output"):
                if isinstance(v, (LightweightMatrixDTO, LightweightMatrixOutput)) or v is None:
                    matrix_reducer_output = v
                elif isinstance(v, Mapping):
                    matrix_reducer_output = TypeAdapter(LightweightMatrixDTO | LightweightMatrixOutput).validate_python(
                        v
                    )
            elif k == "report_context":
                report_context = v
            elif k == "step_detector":
                step_detector = v
            elif k == "evaluated_matrices":
                evaluated_matrices = v
            else:
                variables[k] = v

        return cls(
            global_atom_blackboard=global_atom_blackboard,
            matrix_reducer_output=matrix_reducer_output,
            report_context=report_context,
            step_detector=step_detector,
            evaluated_matrices=evaluated_matrices,
            variables=variables,
        )

    def __getitem__(self, key: str) -> object:
        """Allow subscript access for backward-compatible blackboard lookups."""
        if key in ("__GLOBAL_ATOM_BLACKBOARD__", "global_atom_blackboard"):
            if self.global_atom_blackboard is not None:
                return self.global_atom_blackboard
            if key in self.variables:
                return self.variables[key]
            return None
        if key in ("__MATRIX_REDUCER_OUTPUT__", "matrix_reducer_output"):
            if self.matrix_reducer_output is not None:
                return self.matrix_reducer_output
            if key in self.variables:
                return self.variables[key]
            return None
        if key == "report_context":
            if self.report_context is not None:
                return self.report_context
            if key in self.variables:
                return self.variables[key]
            return None
        if key == "step_detector":
            if self.step_detector is not None:
                return self.step_detector
            if key in self.variables:
                return self.variables[key]
            return None
        if key == "evaluated_matrices":
            if self.evaluated_matrices is not None:
                return self.evaluated_matrices
            if key in self.variables:
                return self.variables[key]
            return None
        if key in self.variables:
            return self.variables[key]
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        """Allow membership checks."""
        if not isinstance(key, str):
            return False
        if key in ("__GLOBAL_ATOM_BLACKBOARD__", "global_atom_blackboard") and self.global_atom_blackboard is not None:
            return True
        if key in ("__MATRIX_REDUCER_OUTPUT__", "matrix_reducer_output") and self.matrix_reducer_output is not None:
            return True
        if key == "report_context" and self.report_context is not None:
            return True
        if key == "step_detector" and self.step_detector is not None:
            return True
        if key == "evaluated_matrices" and self.evaluated_matrices is not None:
            return True
        return key in self.variables
