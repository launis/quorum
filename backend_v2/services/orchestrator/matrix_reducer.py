"""Synchronous reduction of three-state logic (Passed, Failed, DLQ)."""

import logging
from typing import Any, Literal

from pydantic import BaseModel, TypeAdapter, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.matrix import TDAAssertion
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO, ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus

logger = logging.getLogger(__name__)

State = Literal["PASSED", "FAILED", "DLQ"]
_dict_adapter: TypeAdapter[dict[str, Any]] = TypeAdapter(dict[str, Any])


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

        Primary extraction reads evaluated atoms from ExecutionRecord.execution_trace
        events with event_type="output" and "results" list. Falls back to inspecting
        record.step_states scorecard_atoms for backward compatibility with mock fixtures.

        Args:
            record: The modern ExecutionRecord containing execution_trace and step_states.

        Returns:
            A token-compressed LightweightMatrixDTO for the synthesis phase.
        """
        reduced_atoms: list[ReducedAtomDTO] = []
        total_atoms = 0
        evaluated_matrix_ids: set[str] = set()
        seen_tda_ids: set[str] = set()
        raw_extensions: list[dict[str, Any]] = []

        # 1. Primary: Extract evaluated atoms and extensions from execution_trace (real DAG runtime)
        for evt in record.execution_trace:
            if evt.event_type != "output":
                continue
            try:
                raw_content = evt.content.model_dump() if isinstance(evt.content, BaseModel) else evt.content
                content = _dict_adapter.validate_python(raw_content)
            except ValidationError:
                continue

            # Check if this output event contains evaluated atom results
            results = content.get("results")
            if isinstance(results, list):
                for raw in results:
                    try:
                        atom = (
                            raw if isinstance(raw, AtomResultDTO) else AtomResultDTO.model_validate(raw, strict=False)
                        )
                    except ValidationError as e:
                        logger.warning("[MatrixReducer] Failed to validate AtomResultDTO from trace: %s", e)
                        continue

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

                    # Token-compression cascade: Drop boolean PASSED atoms
                    # to save context window, unless they have extracted quantitative data
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

            # Extract step-level extensions
            for _, val in content.items():
                try:
                    val_dict = _dict_adapter.validate_python(val)
                    exts = val_dict.get("extensions")
                    if isinstance(exts, list):
                        raw_extensions.extend(exts)
                except ValidationError:
                    pass

        # 2. Fallback: If no atoms in execution_trace, inspect step_states (mock test fixtures)
        if total_atoms == 0 and record.step_states:
            for step_state in record.step_states.values():
                for atom_id, sc_atom in step_state.scorecard_atoms.items():
                    total_atoms += 1
                    if not sc_atom.status:
                        continue

                    has_extracted_data = bool(sc_atom.extracted_facts)
                    if sc_atom.status == ExecutionStatus.PASSED and not has_extracted_data:
                        continue

                    source_quote: str | None = None
                    if sc_atom.exact_quotes:
                        first_quote = sc_atom.exact_quotes[0]
                        if isinstance(first_quote, QuoteEvidenceDTO):
                            source_quote = first_quote.quote
                        elif isinstance(first_quote, str):
                            source_quote = first_quote

                    extracted_data: dict[str, Any] | None = None
                    if sc_atom.extracted_facts:
                        extracted_data = sc_atom.extracted_facts

                    reduced_atoms.append(
                        ReducedAtomDTO(
                            tda_id=atom_id,
                            status=sc_atom.status,
                            reasoning=sc_atom.semantic_reasoning,
                            source_quote=source_quote,
                            extracted_data=extracted_data,
                        )
                    )

        if total_atoms > 0 and not evaluated_matrix_ids:
            evaluated_matrix_ids.add("matrix_evaluation")

        logger.info("[MatrixReducer] Reduced %d atoms to %d for synthesis.", total_atoms, len(reduced_atoms))

        evaluated_matrices = [{"matrix_id": mid} for mid in sorted(list(evaluated_matrix_ids))]
        global_metrics: dict[str, Any] = {
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
