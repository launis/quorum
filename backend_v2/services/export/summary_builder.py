"""Tabular summary scorecard dataset builder for Excel Tab 1."""

from __future__ import annotations

from backend_v2.models.dtos.export import ExportMatrixSummaryRowDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.services.export.metadata_resolver import resolve_context_target
from backend_v2.services.export_evidence_formatter import (
    clean_citation_brackets,
    format_ai_reasoning,
)

__all__ = ["build_summary_dtos"]


def build_summary_dtos(
    effective_matrices: list[MatrixScorecardRowDTO],
    locale: str,
    target_id: str,
) -> list[ExportMatrixSummaryRowDTO]:
    """Constructs 13-column summary DTOs for each matrix row in Tab 1.

    Args:
        effective_matrices: Authoritative list of matrix scorecard rows.
        locale: Target localization code ('fi' or 'en').
        target_id: Canonical execution identifier.

    Returns:
        List of strictly validated ExportMatrixSummaryRowDTO instances.
    """
    summary_dtos: list[ExportMatrixSummaryRowDTO] = []
    for m in effective_matrices:
        lbl = m.label_i18n.resolve(target_locale=locale)
        if not lbl:
            lbl = m.name
        ctx_target = resolve_context_target(m, locale)
        dist = ""
        if m.level_breakdown:
            dist = ", ".join(f"{lvl}: {val}" for lvl, val in m.level_breakdown.items())

        true_atoms_val = 0
        if m.true_atoms is not None:
            true_atoms_val = m.true_atoms

        total_atoms_val = 0
        if m.total_atoms is not None:
            total_atoms_val = m.total_atoms

        hit_ratio_val = 0.0
        if total_atoms_val > 0:
            hit_ratio_val = float(true_atoms_val / total_atoms_val)

        raw_score_val = 0.0
        if m.raw_score is not None:
            raw_score_val = m.raw_score
        elif m.score is not None:
            raw_score_val = m.score

        scale_max_val = 0.0
        if m.scale_max is not None:
            scale_max_val = m.scale_max

        norm_score_val = 0.0
        if m.normalized_score is not None:
            norm_score_val = m.normalized_score

        row_expl = format_ai_reasoning(m.row_explanation)
        criteria_val = f"{true_atoms_val}/{total_atoms_val}"

        source_val = ""
        if m.cited_source_title:
            source_val = clean_citation_brackets(m.cited_source_title)
        elif m.cited_source_id:
            source_val = clean_citation_brackets(m.cited_source_id)

        summary_dtos.append(
            ExportMatrixSummaryRowDTO(
                execution_id=target_id,
                label=lbl,
                context_target=ctx_target,
                distribution=dist,
                hits=true_atoms_val,
                total_atoms=total_atoms_val,
                hit_ratio=hit_ratio_val,
                raw_score=raw_score_val,
                scale_max=scale_max_val,
                normalized_score=norm_score_val,
                row_explanation=row_expl,
                criteria=criteria_val,
                source=source_val,
            )
        )
    return summary_dtos
