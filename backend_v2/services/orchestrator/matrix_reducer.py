"""Synchronous reduction of three-state logic (Passed, Failed, DLQ)."""

from __future__ import annotations

import logging
from typing import Any, Literal

from pydantic import BaseModel, JsonValue, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.matrix import TDAAssertion
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO, ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import StepOutputDTO

logger = logging.getLogger(__name__)

type State = Literal["PASSED", "FAILED", "DLQ"]

__all__ = ["MatrixReducer", "State"]


class MatrixReducer:
    """Evaluates the final state of an assertion based on its evaluated chunks/atoms.

    Implements Three-State Logic (Passed, Failed, DLQ).
    Also implements Token-compression strategies for the Synthesis LLM.
    """

    @staticmethod
    def reduce_exists(states: list[State]) -> State:
        """ANY(Passed) -> Passed. ALL(Failed) -> Failed. Else DLQ.

        Args:
            states: A list of evaluated chunk states.

        Returns:
            The reduced three-state logic result (PASSED, FAILED, or DLQ).
        """
        if not states:
            return "DLQ"
        if "PASSED" in states:
            return "PASSED"
        if all(s == "FAILED" for s in states):
            return "FAILED"
        return "DLQ"

    @staticmethod
    def reduce_all_must_comply(states: list[State]) -> State:
        """1. ANY(Failed) -> Failed. 2. ANY(DLQ) -> DLQ. 3. ALL(Passed) -> Passed.

        Args:
            states: A list of evaluated chunk states.

        Returns:
            The reduced three-state logic result (PASSED, FAILED, or DLQ).
        """
        if not states:
            return "DLQ"
        if "FAILED" in states:
            return "FAILED"
        if "DLQ" in states:
            return "DLQ"
        return "PASSED"

    @classmethod
    def reduce(cls, assertion: TDAAssertion, states: list[State]) -> State:
        """Reduces states according to the assertion's aggregation_mode.

        Args:
            assertion: The TDAAssertion definition.
            states: A list of evaluated chunk states.

        Returns:
            The reduced three-state logic result.

        Raises:
            AppException: If the aggregation mode is unknown (ErrorCodes.VALIDATION_FAILED).
        """
        match assertion.aggregation_mode:
            case "EXISTS":
                return cls.reduce_exists(states)
            case "ALL_MUST_COMPLY":
                return cls.reduce_all_must_comply(states)
            case _:
                msg = f"Unknown aggregation mode: {assertion.aggregation_mode}"
                logger.error("[MatrixReducer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

    @staticmethod
    def reduce_matrix(record: ExecutionRecord) -> LightweightMatrixDTO:
        """Filters out PASSED atoms to save Context Window space for Synthesis LLM.

        Primary extraction reads evaluated atoms from ExecutionRecord.execution_trace
        events with event_type="output" and "results" list.

        Args:
            record: The modern ExecutionRecord containing execution_trace.

        Returns:
            A token-compressed LightweightMatrixDTO for the synthesis phase.

        Raises:
            AppException: If an atom result in the execution trace fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        reduced_atoms: list[ReducedAtomDTO] = []
        total_atoms = 0
        evaluated_matrix_ids: set[str] = set()
        seen_tda_ids: set[str] = set()
        raw_extensions: list[dict[str, Any]] = []

        # 1. Primary: Extract evaluated atoms and extensions from execution_trace (real DAG runtime)
        for evt in record.execution_trace:
            if evt.event_type != "output" or evt.content is None:
                continue

            results_list: list[Any] | None = None
            if isinstance(evt.content, StepOutputDTO):
                if type(evt.content.payload) is dict and "results" in evt.content.payload:
                    res = evt.content.payload["results"]
                    if isinstance(res, list):
                        results_list = res
                elif isinstance(evt.content.payload, list):
                    results_list = evt.content.payload
            elif type(evt.content) is dict:
                if "results" in evt.content and isinstance(evt.content["results"], list):
                    results_list = evt.content["results"]
                # Extract step-level extensions
                for val in evt.content.values():
                    if type(val) is dict and "extensions" in val and isinstance(val["extensions"], list):
                        raw_extensions.extend(val["extensions"])
            elif isinstance(evt.content, BaseModel):
                dumped = evt.content.model_dump()
                if "results" in dumped and isinstance(dumped["results"], list):
                    results_list = dumped["results"]
                for val in dumped.values():
                    if type(val) is dict and "extensions" in val and isinstance(val["extensions"], list):
                        raw_extensions.extend(val["extensions"])

            if results_list is not None:
                for raw in results_list:
                    try:
                        atom = (
                            raw if isinstance(raw, AtomResultDTO) else AtomResultDTO.model_validate(raw, strict=False)
                        )
                    except ValidationError as e:
                        msg = f"Failed to validate AtomResultDTO from execution trace: {e}"
                        logger.error("[MatrixReducer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from e

                    if atom.tda_id in seen_tda_ids:
                        continue
                    seen_tda_ids.add(atom.tda_id)
                    total_atoms += 1

                    if isinstance(atom.matrix_id, str) and atom.matrix_id.strip():
                        evaluated_matrix_ids.add(atom.matrix_id.strip())
                    elif isinstance(evt.step_name, str) and evt.step_name.strip():
                        evaluated_matrix_ids.add(evt.step_name.strip())

                    if atom.extensions:
                        raw_extensions.append(atom.extensions)

                    # Token-compression cascade: Drop unstarted/pending atoms and boolean PASSED atoms
                    # to save context window, unless they have extracted quantitative data
                    if atom.status in (ExecutionStatus.PENDING, ExecutionStatus.QUEUED, ExecutionStatus.RUNNING):
                        continue

                    has_extracted_data = atom.extracted_data is not None
                    if atom.status == ExecutionStatus.PASSED and not has_extracted_data:
                        continue

                    extracted_data_dict: dict[str, Any] | None = None
                    if atom.extracted_data:
                        extracted_data_dict = atom.extracted_data.model_dump(mode="json")

                    reduced_atoms.append(
                        ReducedAtomDTO(
                            tda_id=atom.tda_id,
                            status=atom.status,
                            reasoning=atom.evaluation_reasoning,
                            source_quote=atom.source_quote,
                            extracted_data=extracted_data_dict,
                        )
                    )

        if total_atoms > 0 and not evaluated_matrix_ids:
            evaluated_matrix_ids.add("matrix_evaluation")

        logger.info("[MatrixReducer] Reduced %d atoms to %d for synthesis.", total_atoms, len(reduced_atoms))

        evaluated_matrices: list[dict[str, JsonValue]] = [
            {"matrix_id": mid} for mid in sorted(list(evaluated_matrix_ids))
        ]
        global_metrics: dict[str, JsonValue] = {
            "total_atoms": total_atoms,
            "evaluated": total_atoms,
            "duration_ms": record.duration_ms,
        }

        return LightweightMatrixDTO(
            execution_id=record.id,
            reduced_atoms=reduced_atoms,
            global_metrics=global_metrics,
            evaluated_matrices=evaluated_matrices,
            raw_extensions=raw_extensions,
        )
