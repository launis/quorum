"""Synchronous reduction of three-state logic (Passed, Failed, DLQ)."""

import logging
from typing import Any, Literal

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixDTO, ReducedAtomDTO
from backend_v2.models.v2_core import ExecutionRecord, TDAAssertion

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
    def reduce_matrix(record: ExecutionRecord) -> LightweightMatrixDTO:
        """Filters out PASSED atoms to save Context Window space for Synthesis LLM.

        Iterates directly over ExecutionRecord.step_states → scorecard_atoms,
        bypassing the need for V3ResultProjector.

        Args:
            record: The modern ExecutionRecord containing step_states with scorecard_atoms.

        Returns:
            A token-compressed LightweightMatrixDTO for the synthesis phase.
        """
        reduced_atoms: list[ReducedAtomDTO] = []
        total_atoms = 0

        for step_state in record.step_states.values():
            for atom_id, atom in step_state.scorecard_atoms.items():
                total_atoms += 1
                status_str = atom.status if isinstance(atom.status, str) else str(atom.status)

                # Token-compression cascade: Drop boolean PASSED atoms
                # to save context window, unless they have extracted quantitative data
                has_extracted_data = bool(atom.extracted_facts)
                if status_str == "PASS" and not has_extracted_data:
                    continue

                # Extract first quote text if available
                source_quote: str | None = None
                if atom.exact_quotes:
                    first_quote = atom.exact_quotes[0]
                    source_quote = first_quote.quote if hasattr(first_quote, "quote") else None

                extracted_data: dict[str, Any] | None = atom.extracted_facts if atom.extracted_facts else None

                reduced_atom = ReducedAtomDTO(
                    tda_id=atom_id,
                    status=status_str,
                    reasoning=atom.semantic_reasoning,
                    source_quote=source_quote,
                    extracted_data=extracted_data,
                )
                reduced_atoms.append(reduced_atom)

        logger.info("[MatrixReducer] Reduced %d atoms to %d for synthesis.", total_atoms, len(reduced_atoms))

        # Build dynamic global metrics from the step_states
        evaluated = total_atoms
        global_metrics: dict[str, Any] = {
            "total_atoms": total_atoms,
            "evaluated": evaluated,
            "duration_ms": record.duration_ms,
        }

        return LightweightMatrixDTO(
            execution_id=record.id,
            reduced_atoms=reduced_atoms,
            global_metrics=global_metrics,
        )
