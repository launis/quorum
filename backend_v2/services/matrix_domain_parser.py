"""Matrix Domain Parser Service."""

from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, MatrixPromptBlock
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.dtos.matrix_parser import ParsedMatricesResultDTO, ScorecardAtomCollectionDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.localization import LocalizationService
from backend_v2.services.matrix_parser.distribution_formatter import (
    clean_hallucinated_numbers,
    format_level_breakdown,
    format_level_distribution,
    resolve_row_explanation,
)
from backend_v2.services.matrix_parser.scale_and_atom_stage import (
    compute_scale_and_score_projection,
    hydrate_step_scorecard_atoms,
    unpack_matrix_payload,
)

__all__ = ["MatrixDomainParser"]

logger = logging.getLogger(__name__)


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

            if not pb_meta.label:
                logger.error(
                    "[MatrixDomainParser] %s: Fail-Fast: PromptBlock '%s' is missing a required I18n label.",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    b_id,
                )
                raise AppException(
                    message=f"Fail-Fast: PromptBlock '{b_id}' is missing a required I18n label.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            axis_name = pb_meta.label.resolve(locale)
            if not axis_name:
                axis_name = b_id

            axis_description = ""
            if pb_meta.description:
                axis_description = pb_meta.description.resolve(locale)

            scale_proj = compute_scale_and_score_projection(
                matrix_payload=matrix_payload,
                pb_meta=pb_meta,
                profile=profile,
                locale=locale,
                block_id=b_id,
            )

            original_axis_name = axis_name
            collision_counter = 1
            while any(ext.name == axis_name for ext in all_parsed_matrices.values()):
                step_node = workflow_steps[step_id]
                step_title = step_node.id
                axis_name = f"{original_axis_name} ({step_title})"
                if any(ext.name == axis_name for ext in all_parsed_matrices.values()):
                    axis_name = f"{original_axis_name} ({step_title} {collision_counter})"
                    collision_counter += 1

            # Phase 1, Step 3: Delegate level breakdown and row explanation formatting
            axis_level_breakdown = format_level_breakdown(matrix_payload.level_breakdown, locale, b_id)

            ext = matrix_payload.extensions

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

            # Inner SDUI blocks reserved for presentation layer rendering
            inner_sdui_blocks: list[AnySduiBlock] = []

            # Three-Tier Deterministic Context Target Resolution
            context_target: str | None = None
            context_target_label: I18nText | None = None
            step_rule: StepRule | None = None
            if step_id in workflow_steps:
                step_rule = workflow_steps[step_id]

            step_input_keys: list[str] = []
            if step_rule and step_rule.input_mappings:
                for mapped_val in step_rule.input_mappings.values():
                    if isinstance(mapped_val, str):
                        val_clean = mapped_val.strip()
                        if val_clean.startswith("$inputs."):
                            clean_key = val_clean.removeprefix("$inputs.").strip()
                            if expected_inputs_map is None or clean_key in expected_inputs_map:
                                if clean_key not in step_input_keys:
                                    step_input_keys.append(clean_key)
                        elif expected_inputs_map is not None and val_clean in expected_inputs_map:
                            if val_clean not in step_input_keys:
                                step_input_keys.append(val_clean)
                        elif expected_inputs_map is None and "$" not in val_clean:
                            # Harness compatibility for isolated unit tests lacking expected_inputs_map
                            if val_clean not in step_input_keys:
                                step_input_keys.append(val_clean)

            # Tier 1: Single-Input Step
            if len(step_input_keys) == 1:
                context_target = step_input_keys[0]
            # Tier 2: Multi-Input Step with Explicit Matrix SSOT
            elif len(step_input_keys) > 1:
                target_key = pb_meta.target_input_key
                if target_key in ("chat_log", "product_text"):
                    context_target = target_key
                else:
                    context_target = "all"
            elif pb_meta.target_input_key is not None:
                context_target = pb_meta.target_input_key

            # Tier 3: Label Resolution
            if context_target is not None:
                input_def = None
                if expected_inputs_map and context_target in expected_inputs_map:
                    input_def = expected_inputs_map[context_target]

                if input_def and input_def.label:
                    context_target_label = input_def.label
                elif context_target in ("all", "chat_log", "product_text"):
                    l10n_key = f"matrix_target_{context_target}"
                    fi_label = LocalizationService.translate(l10n_key, "fi")
                    en_label = LocalizationService.translate(l10n_key, "en")
                    context_target_label = I18nText(translations={"fi": fi_label, "en": en_label})
                else:
                    context_target_label = I18nText(translations={"fi": context_target, "en": context_target})

            remediation_steps = None
            coaching = None
            falsification = None
            evidence_type = None
            cited_source_id = None
            cited_text_quote = None
            cited_web_citation = None
            confidence = None
            contextual_override = None

            if ext is not None:
                remediation_steps = ext.remediation_steps
                coaching = ext.coaching
                falsification = ext.falsification
                evidence_type = ext.evidence_type
                cited_source_id = ext.source_id
                cited_text_quote = ext.citation
                cited_web_citation = ext.google_citation
                confidence = ext.confidence
                contextual_override = ext.contextual_override

            cited_source_title = None
            if pb_meta.theory_grounding and pb_meta.theory_grounding.citation_reference:
                cited_source_title = pb_meta.theory_grounding.citation_reference

            cited_source_url = None
            if pb_meta.theory_grounding and pb_meta.theory_grounding.source_url:
                cited_source_url = pb_meta.theory_grounding.source_url
            elif ext and ext.google_citation:
                cited_source_url = ext.google_citation

            row_semantic_reasoning: str | None = matrix_payload.justification
            if ext and ext.semantic_reasoning:
                row_semantic_reasoning = ext.semantic_reasoning

            validated_evidence_type: Literal["EXPLICIT_QUOTE", "IMPLIED_INTENT", "NO_EVIDENCE"] | None = None
            if evidence_type == "EXPLICIT_QUOTE":
                validated_evidence_type = "EXPLICIT_QUOTE"
            elif evidence_type == "IMPLIED_INTENT":
                validated_evidence_type = "IMPLIED_INTENT"
            elif evidence_type == "NO_EVIDENCE":
                validated_evidence_type = "NO_EVIDENCE"

            row_dto = MatrixScorecardRowDTO(
                block_id=b_id,
                name=axis_name,
                label_i18n=pb_meta.label,
                description=axis_description,
                score=scale_proj.score_float,
                raw_score=scale_proj.raw_score,
                raw_scale_min=scale_proj.math_min,
                raw_scale_max=scale_proj.math_max,
                score_display_label=scale_proj.score_display_label,
                scale_min=scale_proj.display_scale_min,
                scale_max=scale_proj.display_scale_max,
                normalized_score=scale_proj.norm_score,
                true_atoms=scale_proj.true_atoms,
                total_atoms=scale_proj.total_atoms,
                row_explanation=cleaned_explanation,
                evidence_type=validated_evidence_type,
                cited_source_id=cited_source_id,
                cited_text_quote=cited_text_quote,
                cited_web_citation=cited_web_citation,
                cited_source_title=cited_source_title,
                cited_source_url=cited_source_url,
                context_target=context_target,
                context_target_label=context_target_label,
                remediation_steps=remediation_steps,
                coaching=coaching,
                falsification=falsification,
                confidence=confidence,
                contextual_override=contextual_override,
                semantic_reasoning=row_semantic_reasoning,
                level_breakdown=axis_level_breakdown,
                level_names=scale_proj.level_names,
                ui_boundary_labels=scale_proj.ui_boundary_labels,
                ui_plot_ratio=scale_proj.ui_plot_ratio,
                is_evaluative=pb_meta.is_evaluative,
                allow_contextual_override=pb_meta.allow_contextual_override,
                evaluated_atoms=atom_hydration.evaluated_atoms,
                clustered_row_sources=atom_hydration.clustered_row_sources,
                used_evidence_ids=[],
                inner_sdui_blocks=inner_sdui_blocks,
                tda_state=None,
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
