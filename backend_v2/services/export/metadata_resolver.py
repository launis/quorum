"""Metadata resolver for forensic export compilation.

Provides stateless leaf functions for resolving matrix labels, scale metadata,
atom lookups, context targets, and causal graph artifacts.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
)
from backend_v2.models.dtos.causal_discovery import (
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
)
from backend_v2.models.dtos.export import (
    AtomCausalMetadataDTO,
    AtomScaleMetadataDTO,
)
from backend_v2.models.dtos.matrix_scorecard import (
    MatrixScorecardRowDTO,
    ScorecardAtomDTO,
)
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.enums import ExecutionStatus

if TYPE_CHECKING:
    from backend_v2.models.domain.execution import ExecutionRecord

logger = logging.getLogger(__name__)

__all__ = [
    "build_matrix_atom_maps",
    "build_scale_metadata",
    "extract_causal_result",
    "resolve_causal_meta",
    "resolve_context_target",
    "resolve_matrix_label",
]


def build_matrix_atom_maps(
    effective_matrices: list[MatrixScorecardRowDTO],
) -> tuple[dict[str, MatrixScorecardRowDTO], dict[str, ScorecardAtomDTO]]:
    """Maps atom IDs to their parent matrices and scorecard atom records.

    Args:
        effective_matrices: List of evaluated matrix scorecard rows.

    Returns:
        Tuple of atom-to-matrix and atom-to-scorecard-atom lookup dictionaries.
    """
    atom_to_matrix: dict[str, MatrixScorecardRowDTO] = {}
    atom_to_scorecard: dict[str, ScorecardAtomDTO] = {}
    for m in effective_matrices:
        for s_atom in m.evaluated_atoms:
            atom_to_matrix[s_atom.atom_id] = m
            atom_to_scorecard[s_atom.atom_id] = s_atom
    return atom_to_matrix, atom_to_scorecard


def build_scale_metadata(
    blocks_by_id: dict[str, AnyPromptBlock],
    locale: str,
) -> dict[str, AtomScaleMetadataDTO]:
    """Indexes scale and claim metadata by TDA atom assertion ID.

    Args:
        blocks_by_id: Pre-indexed prompt blocks dictionary.
        locale: Target localization code ('fi' or 'en').

    Returns:
        Dictionary mapping TDA assertion IDs to scale metadata DTOs.
    """
    atom_scale_meta: dict[str, AtomScaleMetadataDTO] = {}
    for b in blocks_by_id.values():
        if isinstance(b, MatrixPromptBlock) and b.scales:
            for scale in b.scales:
                scale_lvl = scale.score
                scale_name = scale.ai_label
                if scale.name is not None:
                    scale_name = scale.name.resolve(target_locale=locale)
                for claim in scale.claims:
                    claim_desc = claim.label.resolve(target_locale=locale)
                    for tda in claim.tda_assertions:
                        atom_scale_meta[tda.tda_id] = AtomScaleMetadataDTO(
                            matrix_id=b.id,
                            level=scale_lvl,
                            level_name=scale_name,
                            criterion=claim_desc,
                            is_inverse=bool(tda.inverse_evidence),
                        )
    return atom_scale_meta


def resolve_matrix_label(
    atom_matrix_id: str | None,
    tda_id: str,
    parent_m: MatrixScorecardRowDTO | None,
    matrix_title_lookup: dict[str, str],
    blocks_by_id: dict[str, AnyPromptBlock],
    atom_scale_meta: dict[str, AtomScaleMetadataDTO],
    locale: str,
) -> str:
    """Resolves localized parent matrix label for an evaluated atom.

    Args:
        atom_matrix_id: Matrix block ID declared on the atom result.
        tda_id: TDA assertion identifier.
        parent_m: Parent matrix row DTO if matched.
        matrix_title_lookup: Pre-computed matrix titles by block ID.
        blocks_by_id: Pre-indexed prompt blocks dictionary.
        atom_scale_meta: Pre-indexed atom scale metadata dictionary.
        locale: Target localization code ('fi' or 'en').

    Returns:
        Resolved localized matrix title string.

    Raises:
        AppException: If matrix definition cannot be found in available lookups (RESOURCE_NOT_FOUND).
    """
    if atom_matrix_id:
        if atom_matrix_id in matrix_title_lookup:
            return matrix_title_lookup[atom_matrix_id]
        if atom_matrix_id in blocks_by_id:
            return blocks_by_id[atom_matrix_id].label.resolve(target_locale=locale)
        if parent_m is not None:
            lbl = parent_m.label_i18n.resolve(target_locale=locale)
            if lbl:
                return lbl
            return parent_m.name
    elif parent_m is not None:
        lbl = parent_m.label_i18n.resolve(target_locale=locale)
        if lbl:
            return lbl
        return parent_m.name
    elif tda_id in atom_scale_meta:
        meta = atom_scale_meta[tda_id]
        if meta.matrix_id in matrix_title_lookup:
            return matrix_title_lookup[meta.matrix_id]
        if meta.matrix_id in blocks_by_id:
            return blocks_by_id[meta.matrix_id].label.resolve(target_locale=locale)

    if atom_matrix_id is not None:
        msg = (
            f"Strict Fail-Fast: Matrix block '{atom_matrix_id}' for atom '{tda_id}' "
            "not found in matrices or prompt block repository."
        )
    else:
        msg = f"Strict Fail-Fast: Matrix block for atom '{tda_id}' not found in matrices or prompt block repository."
    logger.error(
        "[ExportService] %s: %s",
        ErrorCodes.RESOURCE_NOT_FOUND.name,
        msg,
        exc_info=True,
        extra={
            "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
            "matrix_id": atom_matrix_id,
            "tda_id": tda_id,
        },
    )
    raise AppException(
        message=msg,
        status_code=404,
        details={
            "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
            "matrix_id": atom_matrix_id,
            "tda_id": tda_id,
        },
    )


def resolve_context_target(parent_m: MatrixScorecardRowDTO | None, locale: str) -> str:
    """Resolves localized context target string from parent matrix row.

    Args:
        parent_m: Parent matrix row DTO or None.
        locale: Target localization code ('fi' or 'en').

    Returns:
        Resolved context target string or empty string.
    """
    if parent_m is None:
        return ""
    if parent_m.context_target_label is not None:
        return parent_m.context_target_label.resolve(target_locale=locale)
    if parent_m.context_target:
        return parent_m.context_target
    return ""


def extract_causal_result(
    execution: ExecutionRecord | None,
) -> CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None:
    """Extracts CausalTdaFusionResultDTO or CausalGraphPayloadDTO from execution trace or step states.

    Args:
        execution: Optional ExecutionRecord to extract causal data from.

    Returns:
        CausalTdaFusionResultDTO or CausalGraphPayloadDTO instance if present, else None.
    """
    if execution is None:
        return None

    for evt in reversed(execution.execution_trace):
        match evt.content:
            case CausalTdaFusionResultDTO() | CausalGraphPayloadDTO():
                return evt.content
            case _:
                continue

    if execution.step_states:
        for state_val in execution.step_states.values():
            if isinstance(state_val, StepOutputDTO):
                match state_val.payload:
                    case CausalTdaFusionResultDTO() | CausalGraphPayloadDTO():
                        return state_val.payload
                    case _:
                        continue
            elif isinstance(state_val, (CausalTdaFusionResultDTO, CausalGraphPayloadDTO)):
                return state_val

    return None


def resolve_causal_meta(
    c_node: CausalNodeDTO | None,
    root_cause_set: set[str],
    isolated_set: set[str],
) -> AtomCausalMetadataDTO:
    """Resolves topological causal metadata for a single argument node.

    Args:
        c_node: Optional CausalNodeDTO instance.
        root_cause_set: Set of node IDs identified as root causes.
        isolated_set: Set of node IDs identified as isolated/orphaned.

    Returns:
        AtomCausalMetadataDTO containing causal_status, blame_parent_id, and dependent_count.
    """
    if c_node is None:
        return AtomCausalMetadataDTO()

    if c_node.node_id in isolated_set:
        status = "orphan"
    elif c_node.status == ExecutionStatus.PASSED:
        status = "validated"
    elif c_node.blame_parent_ids:
        status = "cascading_fault"
    else:
        status = "root_cause"

    blame_parent: str | None = None
    if c_node.blame_parent_ids:
        blame_parent = c_node.blame_parent_ids[0]
    dep_count = len(c_node.dependent_child_ids)

    return AtomCausalMetadataDTO(
        causal_status=status,
        blame_parent_id=blame_parent,
        dependent_count=dep_count,
    )
