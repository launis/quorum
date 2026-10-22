"""Tabular raw atom dataset and denormalized flat row builders.

Extracts granular atom evaluations, forensic quotes, AI reasoning, and causal metadata
for Excel Tab 2 and flat CSV streaming under Single-Pipeline Streaming invariants.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend_v2.models.core_base import coerce_source_quotes_tuple
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.dtos.causal_discovery import (
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
)
from backend_v2.models.dtos.export import (
    AtomScaleMetadataDTO,
    ExportDenormalizedFlatRowDTO,
    ExportForensicAtomDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.export.metadata_resolver import (
    build_matrix_atom_maps,
    build_scale_metadata,
    resolve_causal_meta,
    resolve_context_target,
    resolve_matrix_label,
)
from backend_v2.services.export_evidence_formatter import (
    format_ai_reasoning,
    format_text_observations,
)
from backend_v2.services.localization import LocalizationService

if TYPE_CHECKING:
    pass

__all__ = [
    "build_atom_rows",
    "build_denormalized_rows",
]


def build_atom_rows(
    report_dto: ReportDataDTO,
    matrices: list[MatrixScorecardRowDTO],
    locale: str,
    blocks_by_id: dict[str, AnyPromptBlock],
    matrix_title_lookup: dict[str, str],
    all_matrices: list[MatrixScorecardRowDTO] | None = None,
    causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None,
) -> list[ExportForensicAtomDTO]:
    """Constructs tabular raw data rows containing complete atom details with binary results.

    Args:
        report_dto: ReportDataDTO containing evaluated atom results and references.
        matrices: List of authoritative MatrixScorecardRowDTO instances.
        locale: Target localization code ('fi' or 'en').
        blocks_by_id: Pre-indexed prompt blocks dictionary.
        matrix_title_lookup: Pre-computed matrix titles by block ID.
        all_matrices: Optional comprehensive list of all matrix scorecard rows.
        causal_result: Optional composite fusion or causal graph payload.

    Returns:
        List of strictly validated ExportForensicAtomDTO instances.

    Raises:
        AppException: ErrorCodes.RESOURCE_NOT_FOUND if matrix block for an atom cannot be resolved.
    """
    effective_matrices = matrices
    if all_matrices is not None:
        effective_matrices = all_matrices

    atom_to_matrix, atom_to_scorecard = build_matrix_atom_maps(effective_matrices)
    atom_scale_meta = build_scale_metadata(blocks_by_id, locale)

    causal_nodes_by_id: dict[str, CausalNodeDTO] = {}
    root_cause_set: set[str] = set()
    isolated_set: set[str] = set()
    if causal_result is not None:
        graph = causal_result.graph if isinstance(causal_result, CausalTdaFusionResultDTO) else causal_result
        causal_nodes_by_id = {n.node_id: n for n in graph.nodes}
        root_cause_set = set(graph.root_cause_node_ids)
        isolated_set = set(graph.isolated_node_ids)

    atom_rows: list[ExportForensicAtomDTO] = []
    hydrated_refs = report_dto.hydrated_references

    for atom in report_dto.results:
        parent_m: MatrixScorecardRowDTO | None = None
        if atom.tda_id in atom_to_matrix:
            parent_m = atom_to_matrix[atom.tda_id]

        matrix_label = resolve_matrix_label(
            atom_matrix_id=atom.matrix_id,
            tda_id=atom.tda_id,
            parent_m=parent_m,
            matrix_title_lookup=matrix_title_lookup,
            blocks_by_id=blocks_by_id,
            atom_scale_meta=atom_scale_meta,
            locale=locale,
        )
        context_target = resolve_context_target(parent_m, locale)

        scorecard_atom: ScorecardAtomDTO | None = None
        if atom.tda_id in atom_to_scorecard:
            scorecard_atom = atom_to_scorecard[atom.tda_id]

        meta: AtomScaleMetadataDTO | None = None
        if atom.tda_id in atom_scale_meta:
            meta = atom_scale_meta[atom.tda_id]

        level = 0
        level_name = ""
        if scorecard_atom is not None:
            level = scorecard_atom.level
            level_name = scorecard_atom.level_name
        elif meta is not None:
            level = meta.level
            level_name = meta.level_name

        ref = None
        if hydrated_refs and atom.tda_id in hydrated_refs:
            ref = hydrated_refs[atom.tda_id]

        criterion = ""
        if ref is not None and ref.resolved_claim:
            criterion = ref.resolved_claim
        elif scorecard_atom is not None and scorecard_atom.claim_label:
            criterion = scorecard_atom.claim_label
        elif meta is not None:
            criterion = meta.criterion

        is_inverse_claim = False
        if atom.is_inverse_evidence:
            is_inverse_claim = True
        elif meta is not None and meta.is_inverse:
            is_inverse_claim = True

        is_inverse_val = 1 if is_inverse_claim else 0
        points_awarded_val = 1.0 if (atom.status == ExecutionStatus.PASSED and not is_inverse_claim) else 0.0

        claim_type = LocalizationService.translate("export_claim_positive", locale)
        if is_inverse_claim:
            claim_type = LocalizationService.translate("export_claim_inverse", locale)

        result_status: int = 0
        if atom.status == ExecutionStatus.PASSED:
            result_status = 1

        quote_raw: tuple[str, ...] | list[str] | str | None = atom.source_quotes
        if quote_raw is None and ref is not None:
            quote_raw = ref.source_quotes
        formatted_quotes = format_text_observations(coerce_source_quotes_tuple(quote_raw))
        formatted_reasoning = format_ai_reasoning(atom.evaluation_reasoning)

        c_node: CausalNodeDTO | None = None
        if atom.tda_id in causal_nodes_by_id:
            c_node = causal_nodes_by_id[atom.tda_id]

        causal_meta = resolve_causal_meta(
            c_node,
            root_cause_set,
            isolated_set,
        )

        atom_rows.append(
            ExportForensicAtomDTO(
                matrix_label=matrix_label,
                context_target=context_target,
                level=level,
                level_name=level_name,
                criterion=criterion,
                claim_type=claim_type,
                is_inverse=is_inverse_val,
                points_awarded=points_awarded_val,
                result_status=result_status,
                quotes=formatted_quotes,
                ai_reasoning=formatted_reasoning,
                causal_status=causal_meta.causal_status,
                blame_parent_id=causal_meta.blame_parent_id,
                dependent_count=causal_meta.dependent_count,
            )
        )

    mapped_tda_ids: set[str] = {atom.tda_id for atom in report_dto.results}
    for node in causal_nodes_by_id.values():
        if node.node_id in mapped_tda_ids:
            continue
        causal_meta = resolve_causal_meta(
            node,
            root_cause_set,
            isolated_set,
        )
        atom_rows.append(
            ExportForensicAtomDTO(
                matrix_label=LocalizationService.translate("export_causal_matrix_label", locale),
                context_target="",
                level=1,
                level_name=LocalizationService.translate("export_causal_level_name", locale),
                criterion=node.claim,
                claim_type=LocalizationService.translate("export_claim_positive", locale),
                is_inverse=0,
                points_awarded=0.0,
                result_status=1 if node.status == ExecutionStatus.PASSED else 0,
                quotes=format_text_observations(coerce_source_quotes_tuple(node.source_quotes)),
                ai_reasoning="",
                causal_status=causal_meta.causal_status,
                blame_parent_id=causal_meta.blame_parent_id,
                dependent_count=causal_meta.dependent_count,
            )
        )
    return atom_rows


def build_denormalized_rows(
    report_dto: ReportDataDTO,
    matrices: list[MatrixScorecardRowDTO],
    locale: str,
    blocks_by_id: dict[str, AnyPromptBlock],
    matrix_title_lookup: dict[str, str],
    execution_id: str,
    all_matrices: list[MatrixScorecardRowDTO] | None = None,
    causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None,
) -> list[ExportDenormalizedFlatRowDTO]:
    """Constructs denormalized rows combining parent matrix metrics and atom evaluations.

    Args:
        report_dto: ReportDataDTO containing evaluated atom results.
        matrices: List of authoritative MatrixScorecardRowDTO instances.
        locale: Target localization code ('fi' or 'en').
        blocks_by_id: Pre-indexed prompt blocks dictionary.
        matrix_title_lookup: Pre-computed matrix titles by block ID.
        execution_id: Unique execution identifier.
        all_matrices: Optional comprehensive list of all matrix scorecard rows.
        causal_result: Optional composite fusion or causal graph payload.

    Returns:
        List of strictly validated ExportDenormalizedFlatRowDTO instances.

    Raises:
        AppException: ErrorCodes.RESOURCE_NOT_FOUND if matrix block for an atom cannot be resolved.
    """
    effective_matrices = matrices
    if all_matrices is not None:
        effective_matrices = all_matrices

    atom_to_matrix, atom_to_scorecard = build_matrix_atom_maps(effective_matrices)
    atom_scale_meta = build_scale_metadata(blocks_by_id, locale)

    causal_nodes_by_id: dict[str, CausalNodeDTO] = {}
    root_cause_set: set[str] = set()
    isolated_set: set[str] = set()
    if causal_result is not None:
        graph = causal_result.graph if isinstance(causal_result, CausalTdaFusionResultDTO) else causal_result
        causal_nodes_by_id = {n.node_id: n for n in graph.nodes}
        root_cause_set = set(graph.root_cause_node_ids)
        isolated_set = set(graph.isolated_node_ids)

    denormalized_rows: list[ExportDenormalizedFlatRowDTO] = []
    hydrated_refs = report_dto.hydrated_references

    for atom in report_dto.results:
        parent_m: MatrixScorecardRowDTO | None = None
        if atom.tda_id in atom_to_matrix:
            parent_m = atom_to_matrix[atom.tda_id]

        matrix_label = resolve_matrix_label(
            atom_matrix_id=atom.matrix_id,
            tda_id=atom.tda_id,
            parent_m=parent_m,
            matrix_title_lookup=matrix_title_lookup,
            blocks_by_id=blocks_by_id,
            atom_scale_meta=atom_scale_meta,
            locale=locale,
        )
        context_target = resolve_context_target(parent_m, locale)

        dist = ""
        hits_val = 0
        total_atoms_val = 0
        hit_ratio_val = 0.0
        raw_score_val = 0.0
        scale_max_val = 0.0
        normalized_score_val = 0.0

        if parent_m is not None:
            if parent_m.level_breakdown:
                dist = ", ".join(f"{lvl}: {val}" for lvl, val in parent_m.level_breakdown.items())
            if parent_m.true_atoms is not None:
                hits_val = parent_m.true_atoms
            if parent_m.total_atoms is not None:
                total_atoms_val = parent_m.total_atoms
            if total_atoms_val > 0:
                hit_ratio_val = float(hits_val / total_atoms_val)
            if parent_m.raw_score is not None:
                raw_score_val = parent_m.raw_score
            elif parent_m.score is not None:
                raw_score_val = parent_m.score
            if parent_m.scale_max is not None:
                scale_max_val = parent_m.scale_max
            if parent_m.normalized_score is not None:
                normalized_score_val = parent_m.normalized_score

        scorecard_atom: ScorecardAtomDTO | None = None
        if atom.tda_id in atom_to_scorecard:
            scorecard_atom = atom_to_scorecard[atom.tda_id]

        meta: AtomScaleMetadataDTO | None = None
        if atom.tda_id in atom_scale_meta:
            meta = atom_scale_meta[atom.tda_id]

        level = 0
        level_name = ""
        if scorecard_atom is not None:
            level = scorecard_atom.level
            level_name = scorecard_atom.level_name
        elif meta is not None:
            level = meta.level
            level_name = meta.level_name

        ref = None
        if hydrated_refs and atom.tda_id in hydrated_refs:
            ref = hydrated_refs[atom.tda_id]

        criterion = ""
        if ref is not None and ref.resolved_claim:
            criterion = ref.resolved_claim
        elif scorecard_atom is not None and scorecard_atom.claim_label:
            criterion = scorecard_atom.claim_label
        elif meta is not None:
            criterion = meta.criterion

        is_inverse_claim = False
        if atom.is_inverse_evidence:
            is_inverse_claim = True
        elif meta is not None and meta.is_inverse:
            is_inverse_claim = True

        is_inverse_val = 1 if is_inverse_claim else 0
        points_awarded_val = 1.0 if (atom.status == ExecutionStatus.PASSED and not is_inverse_claim) else 0.0

        claim_type = LocalizationService.translate("export_claim_positive", locale)
        if is_inverse_claim:
            claim_type = LocalizationService.translate("export_claim_inverse", locale)

        result_status: int = 0
        if atom.status == ExecutionStatus.PASSED:
            result_status = 1

        quote_raw: tuple[str, ...] | list[str] | str | None = atom.source_quotes
        if quote_raw is None and ref is not None:
            quote_raw = ref.source_quotes
        formatted_quotes = format_text_observations(coerce_source_quotes_tuple(quote_raw))
        formatted_reasoning = format_ai_reasoning(atom.evaluation_reasoning)

        c_node: CausalNodeDTO | None = None
        if atom.tda_id in causal_nodes_by_id:
            c_node = causal_nodes_by_id[atom.tda_id]

        causal_meta = resolve_causal_meta(
            c_node,
            root_cause_set,
            isolated_set,
        )

        denormalized_rows.append(
            ExportDenormalizedFlatRowDTO(
                execution_id=execution_id,
                matrix_label=matrix_label,
                context_target=context_target,
                distribution=dist,
                hits=hits_val,
                total_atoms=total_atoms_val,
                hit_ratio=hit_ratio_val,
                raw_score=raw_score_val,
                scale_max=scale_max_val,
                normalized_score=normalized_score_val,
                level=level,
                level_name=level_name,
                criterion=criterion,
                claim_type=claim_type,
                is_inverse=is_inverse_val,
                points_awarded=points_awarded_val,
                result_status=result_status,
                quotes=formatted_quotes,
                ai_reasoning=formatted_reasoning,
                causal_status=causal_meta.causal_status,
                blame_parent_id=causal_meta.blame_parent_id,
                dependent_count=causal_meta.dependent_count,
            )
        )

    mapped_tda_ids: set[str] = {atom.tda_id for atom in report_dto.results}
    for node in causal_nodes_by_id.values():
        if node.node_id in mapped_tda_ids:
            continue
        causal_meta = resolve_causal_meta(
            node,
            root_cause_set,
            isolated_set,
        )
        denormalized_rows.append(
            ExportDenormalizedFlatRowDTO(
                execution_id=execution_id,
                matrix_label=LocalizationService.translate("export_causal_matrix_label", locale),
                context_target="",
                distribution="",
                hits=1 if node.status == ExecutionStatus.PASSED else 0,
                total_atoms=1,
                hit_ratio=1.0 if node.status == ExecutionStatus.PASSED else 0.0,
                raw_score=1.0 if node.status == ExecutionStatus.PASSED else 0.0,
                scale_max=1.0,
                normalized_score=100.0 if node.status == ExecutionStatus.PASSED else 0.0,
                level=1,
                level_name=LocalizationService.translate("export_causal_level_name", locale),
                criterion=node.claim,
                claim_type=LocalizationService.translate("export_claim_positive", locale),
                is_inverse=0,
                points_awarded=0.0,
                result_status=1 if node.status == ExecutionStatus.PASSED else 0,
                quotes=format_text_observations(coerce_source_quotes_tuple(node.source_quotes)),
                ai_reasoning="",
                causal_status=causal_meta.causal_status,
                blame_parent_id=causal_meta.blame_parent_id,
                dependent_count=causal_meta.dependent_count,
            )
        )
    return denormalized_rows
