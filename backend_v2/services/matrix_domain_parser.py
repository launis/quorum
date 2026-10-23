"""Matrix Domain Parser Service."""

from __future__ import annotations

from typing import Any

from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, MatrixPromptBlock
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.dtos.matrix_parser import ParsedMatricesResultDTO, ScorecardAtomCollectionDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.services.matrix_parser.distribution_formatter import (
    clean_hallucinated_numbers,
    format_level_breakdown,
    format_level_distribution,
    resolve_row_explanation,
)
from backend_v2.services.matrix_parser.row_builder_stage import (
    build_matrix_scorecard_row,
    resolve_axis_description,
    resolve_context_target,
    resolve_unique_axis_name,
)
from backend_v2.services.matrix_parser.scale_and_atom_stage import (
    compute_scale_and_score_projection,
    hydrate_step_scorecard_atoms,
    unpack_matrix_payload,
)

__all__ = ["MatrixDomainParser"]


class MatrixDomainParser:
    """Domain Orchestrator for parsing LLM trace results into MatrixScorecardRowDTOs."""

    @staticmethod
    def _format_level_distribution(lvl_data: LevelStatsDTO, locale: str) -> str:
        """Formats the empirical scale distribution according to Model B architecture.

        Args:
            lvl_data: The LevelStatsDTO containing decomposed affirmative and inverse counts.
            locale: Language string ('fi' or 'en').

        Returns:
            Formatted distribution string adhering to Dumb Painter SDUI contract.
        """
        # Phase 1, Step 3: Delegate _format_level_distribution to leaf formatter module
        return format_level_distribution(lvl_data, locale)

    @staticmethod
    def _clean_hallucinated_numbers(text: str) -> str:
        """Removes sentences that contain numeric evaluations to prevent hallucinations.

        Args:
            text: Raw input text.

        Returns:
            Cleaned text string.
        """
        # Phase 1, Step 3: Delegate _clean_hallucinated_numbers to leaf formatter module
        return clean_hallucinated_numbers(text)

    @staticmethod
    def parse_matrices(
        results: list[Any],
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
        execution: Any = None,
        expected_inputs_map: dict[str, ExpectedInput] | None = None,
    ) -> ParsedMatricesResultDTO:
        """Parses folded results into MatrixScorecardRowDTOs.

        Args:
            results: Folded state trace output.
            locale: Desired output locale.
            blocks_by_id: Map of PromptBlock IDs to their definitions.
            workflow_steps: Map of step IDs to their StepRule definitions.
            profile: The OutputProfile determining which extensions and layouts are valid.
            row_explanations_cache: Rendered explanations to override raw LLM justification.
            workflow_ext_values: List of requested workflow-level extension types.
            row_curated_quotes_cache: Cache of curated evidence quotes per matrix row ID.
            has_synthesis_cache: Flag indicating whether synthesis cache is available.
            rejected_evq_ids: Set of IDs for rejected evidence quotes.
            mcp_audit_map: Map of audit trace ID to trace model.
            source_identity_manifest: Optional map of source ID to display names.
            execution: The execution record.
            expected_inputs_map: Optional map of step expected input definitions for target routing.

        Returns:
            A ParsedMatricesResultDTO containing parsed scorecard rows and atom collections.

        Raises:
            AppException: If validation or configuration constraints fail (specifically:
                ErrorCodes.VALIDATION_FAILED, ErrorCodes.CONFIGURATION_ERROR).
        """
        evaluative_matrices: list[MatrixScorecardRowDTO] = []
        informational_matrices: list[MatrixScorecardRowDTO] = []
        all_parsed_matrices: dict[str, MatrixScorecardRowDTO] = {}
        step_scorecard_atoms_accum: dict[str, list[ScorecardAtomDTO]] = {}

        matrix_visible_cols = ["label", "score", "distribution", "row_explanation", "quotes"]

        for dto in results:
            step_id = dto.step_id
            b_id = dto.block_id
            block_data = dto.payload

            pb_meta = None
            if b_id in blocks_by_id:
                pb_meta = blocks_by_id[b_id]
            if not pb_meta or not isinstance(pb_meta, MatrixPromptBlock):
                continue

            # Phase 2, Step 2: Delegate payload unpacking, scale projection, and atom hydration
            matrix_payload = unpack_matrix_payload(block_data, b_id)

            # Phase 3, Step 2: Delegate axis label, description, context target, and row building stages
            axis_name = resolve_unique_axis_name(
                pb_meta=pb_meta,
                block_id=b_id,
                step_id=step_id,
                locale=locale,
                workflow_steps=workflow_steps,
                all_parsed_matrices=all_parsed_matrices,
            )
            axis_description = resolve_axis_description(pb_meta=pb_meta, locale=locale)

            scale_proj = compute_scale_and_score_projection(
                matrix_payload=matrix_payload,
                pb_meta=pb_meta,
                profile=profile,
                locale=locale,
                block_id=b_id,
            )

            # Phase 1, Step 3: Delegate level breakdown and row explanation formatting
            axis_level_breakdown = format_level_breakdown(matrix_payload.level_breakdown, locale, b_id)

            cleaned_explanation = resolve_row_explanation(
                block_id=b_id,
                profile=profile,
                row_explanations_cache=row_explanations_cache,
                has_synthesis_cache=has_synthesis_cache,
                execution=execution,
            )

            atom_hydration = hydrate_step_scorecard_atoms(
                results=results,
                step_id=step_id,
                pb_meta=pb_meta,
                level_names=scale_proj.level_names,
                locale=locale,
                matrix_visible_cols=matrix_visible_cols,
                step_scorecard_atoms_accum=step_scorecard_atoms_accum,
            )

            context_target_res = resolve_context_target(
                step_id=step_id,
                pb_meta=pb_meta,
                workflow_steps=workflow_steps,
                expected_inputs_map=expected_inputs_map,
            )

            row_dto = build_matrix_scorecard_row(
                block_id=b_id,
                axis_name=axis_name,
                axis_description=axis_description,
                pb_meta=pb_meta,
                matrix_payload=matrix_payload,
                scale_proj=scale_proj,
                axis_level_breakdown=axis_level_breakdown,
                cleaned_explanation=cleaned_explanation,
                atom_hydration=atom_hydration,
                context_target_res=context_target_res,
            )

            unique_k = f"{step_id}_{b_id}"
            all_parsed_matrices[unique_k] = row_dto

            if pb_meta.is_evaluative:
                evaluative_matrices.append(row_dto)
            else:
                informational_matrices.append(row_dto)

        step_scorecard_atoms = {
            step_k: ScorecardAtomCollectionDTO(atoms={atom.atom_id: atom for atom in atom_list})
            for step_k, atom_list in step_scorecard_atoms_accum.items()
        }

        return ParsedMatricesResultDTO(
            evaluative_matrices=evaluative_matrices,
            informational_matrices=informational_matrices,
            all_parsed_matrices=all_parsed_matrices,
            step_scorecard_atoms=step_scorecard_atoms,
        )
