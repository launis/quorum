"""Synchronous reduction of three-state logic (Passed, Failed, DLQ)."""

import logging
from typing import Literal

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixDTO, ReducedAtomDTO
from backend_v2.models.dtos.report.root import ReportDataDto
from backend_v2.models.v2_core import TDAAssertion

logger = logging.getLogger(__name__)

State = Literal["PASSED", "FAILED", "DLQ"]


class MatrixReducer:
    """Evaluates the final state of an assertion based on its evaluated chunks/atoms.

    Implements Three-State Logic (Passed, Failed, DLQ).
    Also implements Token-compression strategies for the Synthesis LLM.
    """

    @staticmethod
    def reduce_exists(states: list[State]) -> State:
        """ANY(Passed) -> Passed. ALL(Failed) -> Failed. Else DLQ."""
        if not states:
            return "DLQ"
        if "PASSED" in states:
            return "PASSED"
        if all(s == "FAILED" for s in states):
            return "FAILED"
        return "DLQ"

    @staticmethod
    def reduce_all_must_comply(states: list[State]) -> State:
        """1. ANY(Failed) -> Failed. 2. ANY(DLQ) -> DLQ. 3. ALL(Passed) -> Passed."""
        if not states:
            return "DLQ"
        if "FAILED" in states:
            return "FAILED"
        if "DLQ" in states:
            return "DLQ"
        return "PASSED"

    @classmethod
    def reduce(cls, assertion: TDAAssertion, states: list[State]) -> State:
        """Reduces states according to the assertion's aggregation_mode."""
        if assertion.aggregation_mode == "EXISTS":
            return cls.reduce_exists(states)
        elif assertion.aggregation_mode == "ALL_MUST_COMPLY":
            return cls.reduce_all_must_comply(states)

        raise AppException(
            message=f"Unknown aggregation mode: {assertion.aggregation_mode}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED},
        )

    @staticmethod
    def reduce_matrix(report: ReportDataDto) -> LightweightMatrixDTO:
        """Filters out PASSED atoms to save Context Window space for Synthesis LLM."""
        reduced_atoms = []
        for atom in report.results:
            # Token-compression cascade: Drop boolean PASSED atoms
            # to save context window, unless they have extracted quantitative data
            status_str = atom.status.value if hasattr(atom.status, "value") else str(atom.status)
            if status_str == "PASSED" and atom.extracted_data is None:
                continue

            reduced_atom = ReducedAtomDTO(
                tda_id=atom.tda_id,
                status=status_str,
                reasoning=atom.evaluation_reasoning,
                source_quote=atom.source_quote,
                extracted_data=atom.extracted_data.model_dump() if atom.extracted_data else None,
            )
            reduced_atoms.append(reduced_atom)

        logger.info("[MatrixReducer] Reduced %d atoms to %d for synthesis.", len(report.results), len(reduced_atoms))

        return LightweightMatrixDTO(
            execution_id=report.execution_id,
            reduced_atoms=reduced_atoms,
            global_metrics=report.global_metrics.model_dump(),
        )
