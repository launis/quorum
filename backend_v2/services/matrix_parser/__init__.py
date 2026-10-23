"""Matrix Domain Parser Package Facade."""

from __future__ import annotations

from collections.abc import Sequence

from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, MatrixPromptBlock
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.dtos.matrix_parser import ParsedMatricesResultDTO, ScorecardAtomCollectionDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.step_output import StepOutputDTO

from .distribution_formatter import clean_hallucinated_numbers as clean_hallucinated_numbers
from .distribution_formatter import format_level_breakdown as format_level_breakdown
from .distribution_formatter import format_level_distribution as format_level_distribution
from .distribution_formatter import resolve_row_explanation as resolve_row_explanation
from .row_builder_stage import build_matrix_scorecard_row as build_matrix_scorecard_row
from .row_builder_stage import resolve_axis_description as resolve_axis_description
from .row_builder_stage import resolve_context_target as resolve_context_target
from .row_builder_stage import resolve_unique_axis_name as resolve_unique_axis_name
from .scale_and_atom_stage import compute_scale_and_score_projection as compute_scale_and_score_projection
from .scale_and_atom_stage import hydrate_step_scorecard_atoms as hydrate_step_scorecard_atoms
from .scale_and_atom_stage import unpack_matrix_payload as unpack_matrix_payload

# Phase 4, Step 2: Declare explicit __all__ and redundant import aliases for package facade
__all__ = [
    "MatrixDomainParser",
    "build_matrix_scorecard_row",
    "clean_hallucinated_numbers",
    "compute_scale_and_score_projection",
    "format_level_breakdown",
    "format_level_distribution",
    "hydrate_step_scorecard_atoms",
    "resolve_axis_description",
    "resolve_context_target",
    "resolve_row_explanation",
    "resolve_unique_axis_name",
    "unpack_matrix_payload",
]


class MatrixDomainParser:
    """Domain Orchestrator for parsing LLM trace results into MatrixScorecardRowDTOs."""

    @staticmethod
    def _format_level_distribution(lvl_data: LevelStatsDTO, locale: str) -> str:
        """Formats the empirical scale distribution according to Model B architecture.

        Args:
            lvl_data: LevelStatsDTO containing affirmative and inverse counts.
            locale: Target language locale ('fi' or 'en').

        Returns:
            Formatted distribution string adhering to Dumb Painter SDUI contract.
        """
        return format_level_distribution(lvl_data, locale)

    @staticmethod
    def _clean_hallucinated_numbers(text: str) -> str:
        """Removes sentences that contain numeric evaluations to prevent hallucinations.

        Args:
            text: Raw input text.

        Returns:
            Cleaned text string.
        """
        return clean_hallucinated_numbers(text)

    @staticmethod
    def parse_matrices(
        results: Sequence[StepOutputDTO],
        locale: str,
        blocks_by_id: dict[str, AnyPromptBlock],
        workflow_steps: dict[str, StepRule],
        profile: OutputProfile,
        row_explanations_cache: dict[str, str],
        workflow_ext_values: list[str],
        row_curated_quotes_cache: dict[str, list[str]],
        has_synthesis_cache: bool = True,
        rejected_evq_ids: set[str] | None = None,
        mcp_audit_map: dict[str, MCPAuditTrace] | None = None,
        source_identity_manifest: dict[str, str] | None = None,
        execution: ExecutionRecord | None = None,
        expected_inputs_map: dict[str, ExpectedInput] | None = None,
    ) -> ParsedMatricesResultDTO:
        """Parses folded results into MatrixScorecardRowDTOs.

        Args:
            results: Folded state trace output items (Sequence of StepOutputDTO).
            locale: Desired output locale.
            blocks_by_id: Map of PromptBlock IDs to their definitions.
            workflow_steps: Map of step IDs to their StepRule definitions.
            profile: Active OutputProfile governing extensions and layouts.
            row_explanations_cache: Rendered explanations overriding raw justification.
            workflow_ext_values: Requested workflow-level extension types.
            row_curated_quotes_cache: Curated evidence quotes per matrix row ID.
            has_synthesis_cache: Flag indicating whether synthesis cache is available.
            rejected_evq_ids: Set of IDs for rejected evidence quotes.
            mcp_audit_map: Map of audit trace ID to trace model.
            source_identity_manifest: Optional map of source ID to display names.
            execution: Optional ExecutionRecord instance.
            expected_inputs_map: Optional map of step expected input definitions.

        Returns:
            ParsedMatricesResultDTO containing parsed rows and atom collections.

        Raises:
            AppException: On validation or configuration failures (VALIDATION_FAILED, CONFIGURATION_ERROR).
        """
        evaluative_matrices: list[MatrixScorecardRowDTO] = []
        informational_matrices: list[MatrixScorecardRowDTO] = []
        all_parsed_matrices: dict[str, MatrixScorecardRowDTO] = {}
        atoms_accum: dict[str, list[ScorecardAtomDTO]] = {}
        vis_cols = ["label", "score", "distribution", "row_explanation", "quotes"]

        for dto in results:
            step_id, b_id, block_data = dto.step_id, dto.block_id, dto.payload
            if b_id not in blocks_by_id:
                continue
            pb = blocks_by_id[b_id]
            if not isinstance(pb, MatrixPromptBlock):
                continue

            payload = unpack_matrix_payload(block_data, b_id)
            axis_name = resolve_unique_axis_name(pb, b_id, step_id, locale, workflow_steps, all_parsed_matrices)
            axis_desc = resolve_axis_description(pb, locale)
            proj = compute_scale_and_score_projection(payload, pb, profile, locale, b_id)
            bd = format_level_breakdown(payload.level_breakdown, locale, b_id)
            expl = resolve_row_explanation(b_id, profile, row_explanations_cache, has_synthesis_cache, execution)
            atoms = hydrate_step_scorecard_atoms(results, step_id, pb, proj.level_names, locale, vis_cols, atoms_accum)
            ctx = resolve_context_target(step_id, pb, workflow_steps, expected_inputs_map)
            row_dto = build_matrix_scorecard_row(b_id, axis_name, axis_desc, pb, payload, proj, bd, expl, atoms, ctx)
            all_parsed_matrices[f"{step_id}_{b_id}"] = row_dto
            if pb.is_evaluative:
                evaluative_matrices.append(row_dto)
            else:
                informational_matrices.append(row_dto)

        step_atoms = {k: ScorecardAtomCollectionDTO(atoms={a.atom_id: a for a in v}) for k, v in atoms_accum.items()}
        return ParsedMatricesResultDTO(
            evaluative_matrices=evaluative_matrices,
            informational_matrices=informational_matrices,
            all_parsed_matrices=all_parsed_matrices,
            step_scorecard_atoms=step_atoms,
        )
