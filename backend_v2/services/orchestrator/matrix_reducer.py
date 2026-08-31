"""Synchronous reduction of three-state logic (Passed, Failed, DLQ)."""

import logging
from typing import Any, Literal

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO, ReducedAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus
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
            AppException: If the aggregation mode is unknown.
        """
        match assertion.aggregation_mode:
            case "EXISTS":
                return cls.reduce_exists(states)
            case "ALL_MUST_COMPLY":
                return cls.reduce_all_must_comply(states)
            case _:
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
                if not atom.status:
                    continue

                # Token-compression cascade: Drop boolean PASSED atoms
                # to save context window, unless they have extracted quantitative data
                has_extracted_data = bool(atom.extracted_facts)
                if atom.status == ExecutionStatus.PASSED and not has_extracted_data:
                    continue

                # Extract first quote text if available
                source_quote: str | None = None
                if atom.exact_quotes:
                    first_quote = atom.exact_quotes[0]
                    source_quote = first_quote.quote if isinstance(first_quote, QuoteEvidenceDTO) else None

                extracted_data: dict[str, Any] | None = atom.extracted_facts if atom.extracted_facts else None

                reduced_atom = ReducedAtomDTO(
                    tda_id=atom_id,
                    status=atom.status,
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

        # Extract raw_extensions from execution_trace
        raw_extensions: list[dict[str, Any]] = []
        for evt in record.execution_trace:
            if evt.event_type == "output":
                content = evt.content
                if isinstance(content, BaseModel):
                    content = content.model_dump()
                if not isinstance(content, (str, int, float, bool, list)) and content is not None:
                    try:
                        for _, val in content.items():
                            if not isinstance(val, (str, int, float, bool, list)) and val is not None:
                                try:
                                    exts = val.get("extensions")
                                    if isinstance(exts, list):
                                        raw_extensions.extend(exts)
                                except AttributeError, TypeError:
                                    pass
                    except AttributeError, TypeError:
                        pass

        return LightweightMatrixDTO(
            execution_id=record.id,
            reduced_atoms=reduced_atoms,
            global_metrics=global_metrics,
            raw_extensions=raw_extensions,
        )
