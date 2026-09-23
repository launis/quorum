"""Context variables DTO for orchestrator execution and dynamic blackboard sharing."""

from __future__ import annotations

from collections.abc import ItemsView, KeysView, Mapping, ValuesView
from typing import Annotated, Self

from pydantic import AliasChoices, ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput


class EvaluatedMatrixContextDTO(V2CoreBase):
    """DTO for evaluated matrix context within execution context_variables."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    evaluated_atoms: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Map of atom IDs to evaluation status"),
    ]
    raw_atoms: Annotated[
        list[EvaluatedAtomDTO],
        Field(default_factory=list, description="Raw evaluated atom payloads"),
    ] = Field(default_factory=list)


type ContextVariableValue = DomainInputValue | GlobalAtomBlackboard | LightweightMatrixDTO | EvaluatedMatrixContextDTO
type ContextVariablesUpdateValue = ContextVariableValue | dict[str, ContextVariableValue]

__all__ = ["ContextVariableValue", "ContextVariablesDTO", "ContextVariablesUpdateValue", "EvaluatedMatrixContextDTO"]


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
        dict[str, ContextVariableValue],
        Field(default_factory=dict, description="Typed arbitrary context variables"),
    ] = Field(default_factory=dict)

    def with_update(
        self,
        **updates: ContextVariableValue,
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
        field_updates: dict[str, ContextVariablesUpdateValue] = {}
        var_updates: dict[str, ContextVariableValue] = dict(self.variables)
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

    def __getitem__(self, key: str) -> ContextVariableValue:
        """Retrieve variable by key. Fail-fast with KeyError on absent keys."""
        if key in ("__GLOBAL_ATOM_BLACKBOARD__", "global_atom_blackboard"):
            if self.global_atom_blackboard is not None:
                return self.global_atom_blackboard
            if key in self.variables:
                return self.variables[key]
            raise KeyError(key)
        if key in ("__MATRIX_REDUCER_OUTPUT__", "matrix_reducer_output"):
            if self.matrix_reducer_output is not None:
                return self.matrix_reducer_output
            if key in self.variables:
                return self.variables[key]
            raise KeyError(key)
        if key == "report_context":
            if self.report_context is not None:
                return self.report_context
            if key in self.variables:
                return self.variables[key]
            raise KeyError(key)
        if key == "step_detector":
            if self.step_detector is not None:
                return self.step_detector
            if key in self.variables:
                return self.variables[key]
            raise KeyError(key)
        if key == "evaluated_matrices":
            if self.evaluated_matrices is not None:
                return self.evaluated_matrices
            if key in self.variables:
                return self.variables[key]
            raise KeyError(key)
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

    def _to_view_dict(self) -> dict[str, ContextVariableValue]:
        """Materialize active keys and values for dictionary views."""
        d: dict[str, ContextVariableValue] = dict(self.variables)
        if self.global_atom_blackboard is not None:
            d["__GLOBAL_ATOM_BLACKBOARD__"] = self.global_atom_blackboard
            d["global_atom_blackboard"] = self.global_atom_blackboard
        if self.matrix_reducer_output is not None:
            d["__MATRIX_REDUCER_OUTPUT__"] = self.matrix_reducer_output
            d["matrix_reducer_output"] = self.matrix_reducer_output
        if self.report_context is not None:
            d["report_context"] = self.report_context
        if self.step_detector is not None:
            d["step_detector"] = self.step_detector
        if self.evaluated_matrices is not None:
            d["evaluated_matrices"] = self.evaluated_matrices
        return d

    def __len__(self) -> int:
        """Return total count of distinct keys."""
        return len(self._to_view_dict())

    def keys(self) -> KeysView[str]:
        """Return a view of all present keys."""
        return self._to_view_dict().keys()

    def values(self) -> ValuesView[ContextVariableValue]:
        """Return a view of all present values."""
        return self._to_view_dict().values()

    def items(self) -> ItemsView[str, ContextVariableValue]:
        """Return a view of all present key-value pairs."""
        return self._to_view_dict().items()

    @classmethod
    def empty(cls) -> Self:
        """Convenience constructor for empty blackboard."""
        return cls(variables={})


Mapping.register(ContextVariablesDTO)
