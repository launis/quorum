"""Matrix Domain Parser Service."""

import logging
import re
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, MatrixPromptBlock
from backend_v2.models.dtos.atom_evaluation import (
    ReasoningStepDTO,
)
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import DisplayScale, ExecutionStatus, VisualIntent
from backend_v2.models.v2_core import (
    AtomResultDTO,
    I18nText,
    MatrixScorecardRowDTO,
    MCPAuditTrace,
    OutputProfile,
    ScorecardAtomDTO,
    StepRule,
)
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.utils.math_utils import scale_to_custom_range

__all__ = ["MatrixDomainParser"]

logger = logging.getLogger(__name__)


class MatrixDomainParser:
    """Domain Orchestrator for parsing LLM trace results into MatrixScorecardRowDTOs."""

    @staticmethod
    def _clean_hallucinated_numbers(text: str) -> str:
        """Removes sentences that contain numeric evaluations to prevent hallucinations.

        Args:
            text: Raw input text.

        Returns:
            Cleaned text string.
        """
        if not text:
            return ""

        sentences = re.split(r"(?<=[.!?]) +", text)
        cleaned = []

        # Regex checks for words like taso, tason, tasolle, arvosana,
        # piste etc. followed by an optional colon and a number
        pattern = re.compile(r"(?i)(taso|arvosana|level|piste|score|grade)[a-zäö]*\s*:?\s*\d")

        for s in sentences:
            if not pattern.search(s):
                cleaned.append(s)

        return " ".join(cleaned).strip()

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
        has_synthesis_cache: bool = False,
        rejected_evq_ids: set[str] | None = None,
        mcp_audit_map: dict[str, MCPAuditTrace] | None = None,
        source_identity_manifest: dict[str, str] | None = None,
        execution: Any = None,
        expected_inputs_map: dict[str, Any] | None = None,
    ) -> tuple[
        list[MatrixScorecardRowDTO],
        list[MatrixScorecardRowDTO],
        dict[str, MatrixScorecardRowDTO],
        dict[str, dict[str, ScorecardAtomDTO]],
    ]:
        """Parses folded results into MatrixScorecardRowDTOs.

        Args:
            results: Folded state trace output.
            locale: Desired output locale.
            blocks_by_id: Map of PromptBlock IDs to their definitions.
            workflow_steps: Map of step IDs to their StepRule definitions.
            profile: The OutputProfile determining which extensions and layouts are valid.
            row_explanations_cache: Rendered explanations to override raw LLM justification.
            workflow_ext_values: List of requested workflow-level extension types.
            rejected_evq_ids: Set of IDs for rejected evidence quotes.
            mcp_audit_map: Map of audit trace ID to trace model.
            source_identity_manifest: Optional map of source ID to display names.
            execution: The execution record.

        Returns:
            A tuple of (evaluative_matrices, informational_matrices, all_parsed_matrices, step_scorecard_atoms).

        Raises:
            AppException: If validation or configuration constraints fail.
        """
        evaluative_matrices: list[MatrixScorecardRowDTO] = []
        informational_matrices: list[MatrixScorecardRowDTO] = []
        all_parsed_matrices: dict[str, MatrixScorecardRowDTO] = {}
        step_scorecard_atoms: dict[str, dict[str, ScorecardAtomDTO]] = {}

        # Safe attribute access using V2 Models
        display_scale = profile.display_scale
        matrix_visible_cols = ["label", "score", "distribution", "row_explanation", "quotes"]

        for dto in results:
            step_id = dto.step_id
            b_id = dto.block_id
            block_data = dto.payload

            pb_meta = blocks_by_id.get(b_id)
            if not pb_meta or not isinstance(pb_meta, MatrixPromptBlock):
                continue

            if not isinstance(block_data, dict):
                msg = (
                    f"Strict Fail-Fast: Invalid matrix payload format for '{b_id}': "
                    f"expected dict, got {type(block_data)}"
                )
                logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

            try:
                matrix_payload = TraceMatrixPayloadDTO.model_validate(block_data)
            except Exception as e:
                msg = f"Strict Fail-Fast: Invalid matrix payload format for '{b_id}': {e}"
                logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            true_atoms = None
            total_atoms = None
            raw_score = matrix_payload.raw_score
            norm_score = matrix_payload.normalized_score

            if matrix_payload.evaluated_atoms:
                true_atoms = sum(1 for v in matrix_payload.evaluated_atoms.values() if v == ExecutionStatus.PASSED)
                total_atoms = sum(1 for v in matrix_payload.evaluated_atoms.values() if v != ExecutionStatus.N_A)

                if total_atoms > 0 and raw_score is None:
                    raw_score = true_atoms / total_atoms
                    norm_score = raw_score * 100.0
                elif total_atoms == 0:
                    logger.info(
                        "[MatrixDomainParser] Matrix '%s' evaluated to N_A (total_atoms=0). Bypassing scoring.", b_id
                    )
                    raw_score = None
                    norm_score = None

            axis_name = pb_meta.label.resolve(locale) if pb_meta.label else b_id
            if not axis_name:
                axis_name = b_id

            if not pb_meta.label:
                logger.error(
                    "[MatrixDomainParser] %s: Fail-Fast: PromptBlock '%s' is missing a required I18n label.",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    b_id,
                )
                raise AppException(
                    message=f"Fail-Fast: PromptBlock '{b_id}' is missing a required I18n label.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            axis_description = pb_meta.description.resolve(locale) if pb_meta.description else ""

            if pb_meta.computed_min is None or pb_meta.computed_max is None:
                logger.error(
                    "[MatrixDomainParser] %s: PromptBlock '%s' missing Pydantic computed_min/max.",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    b_id,
                )
                raise AppException(
                    message=f"PromptBlock '{b_id}' missing Pydantic computed_min/max.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            math_min = float(pb_meta.computed_min)
            math_max = float(pb_meta.computed_max)

            scales_def = pb_meta.scales
            if not scales_def:
                logger.error(
                    "[MatrixDomainParser] %s: PromptBlock '%s' initialized as matrix but has no scales.",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    b_id,
                )
                raise AppException(
                    message=f"PromptBlock '{b_id}' initialized as matrix but has no scales.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            level_names: dict[str, str] = {}
            ui_boundary_labels: dict[str, str] = {}
            for s in scales_def:
                s_score = float(s.score)
                if not s.name:
                    logger.error(
                        "[MatrixDomainParser] %s: Fail-Fast: MatrixScale in block '%s' missing 'name'.",
                        ErrorCodes.VALIDATION_FAILED.name,
                        b_id,
                    )
                    raise AppException(
                        message=f"Fail-Fast: MatrixScale in block '{b_id}' missing 'name'.",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                s_label = s.name.resolve(locale)

                int_str = str(int(s_score)) if s_score.is_integer() else str(s_score)
                float_str = str(s_score)
                level_names[int_str] = s_label
                if float_str != int_str:
                    level_names[float_str] = s_label

                if s_score == math_min:
                    ui_boundary_labels["0.0"] = s_label
                if s_score == math_max:
                    ui_boundary_labels["1.0"] = s_label

            display_scale_min = math_min
            display_scale_max = math_max

            active_score_key = "raw_score"
            if display_scale == DisplayScale.NORMALIZED_100:
                active_score_key = "normalized_score"
                display_scale_min = 0.0
                display_scale_max = 100.0
            elif display_scale == DisplayScale.CUSTOM:
                if profile.custom_scale_min is None or profile.custom_scale_max is None:
                    logger.error(
                        "[MatrixDomainParser] %s: OutputProfile '%s' is missing custom_scale_min/max under custom scale.",
                        ErrorCodes.CONFIGURATION_ERROR.name,
                        profile.id,
                    )
                    raise AppException(
                        message=f"OutputProfile '{profile.id}' is missing custom_scale_min/max under custom scale.",
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
                display_scale_min = float(profile.custom_scale_min)
                display_scale_max = float(profile.custom_scale_max)

            if display_scale == DisplayScale.CUSTOM:
                if raw_score is not None:
                    score_float = float(
                        round(
                            scale_to_custom_range(
                                score=float(raw_score),
                                raw_min=math_min,
                                raw_max=math_max,
                                target_min=display_scale_min,
                                target_max=display_scale_max,
                            ),
                            1,
                        )
                    )
                else:
                    score_float = None
            else:
                if active_score_key == "normalized_score":
                    target_val = matrix_payload.normalized_score
                else:
                    target_val = matrix_payload.raw_score

                if target_val is None:
                    target_val = raw_score

                score_float = float(round(float(target_val), 1)) if target_val is not None else None
                if display_scale == DisplayScale.NORMALIZED_100 and score_float is not None:
                    score_float = float(round(score_float))

            ui_plot_ratio = None
            if raw_score is not None:
                if math_max == math_min:
                    ratio = 0.0
                else:
                    ratio = (float(raw_score) - math_min) / (math_max - math_min)
                ui_plot_ratio = float(max(0.0, min(1.0, ratio)))

            original_axis_name = axis_name
            collision_counter = 1
            while any(ext.name == axis_name for ext in all_parsed_matrices.values()):
                step_node = workflow_steps[step_id]
                step_title = step_node.id
                axis_name = f"{original_axis_name} ({step_title})"
                if any(ext.name == axis_name for ext in all_parsed_matrices.values()):
                    axis_name = f"{original_axis_name} ({step_title} {collision_counter})"
                    collision_counter += 1

            axis_level_breakdown = None
            raw_breakdown = matrix_payload.level_breakdown
            if raw_breakdown:
                clean_level_dict = {}
                for lvl_key, lvl_data in raw_breakdown.items():
                    try:
                        f_lvl = float(lvl_key)
                        is_int = f_lvl.is_integer()
                        c_key = str(int(f_lvl)) if is_int else str(lvl_key)
                        hits = lvl_data.hits
                        total = lvl_data.total
                        clean_level_dict[c_key] = f"{hits}/{total}"
                    except ValueError as v_err:
                        logger.error(
                            "[MatrixDomainParser] %s: Fail-Fast: Invalid level key '%s' in matrix breakdown for '%s'.",
                            ErrorCodes.VALIDATION_FAILED.name,
                            lvl_key,
                            b_id,
                            exc_info=True,
                        )
                        raise AppException(
                            message=(f"Fail-Fast: Invalid level key '{lvl_key}' in matrix breakdown for '{b_id}'."),
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from v_err
                axis_level_breakdown = clean_level_dict

            ext = matrix_payload.extensions

            synthesis_expected = profile.requires_row_explanations
            is_data_starved = False
            if execution and execution.profile_syntheses:
                current_cache = execution.profile_syntheses.get(profile.id) or execution.profile_syntheses.get(
                    "default"
                )
                if current_cache and current_cache.data_starvation is not None:
                    is_data_starved = True

            if synthesis_expected and not is_data_starved:
                if b_id not in row_explanations_cache:
                    msg = f"Fail-Fast: row_explanations_cache missing entry for matrix '{b_id}'. Worker synthesis incomplete."
                    logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
                final_explanation = row_explanations_cache[b_id]
            else:
                final_explanation = row_explanations_cache[b_id] if b_id in row_explanations_cache else ""

            evaluated_atoms_list = []
            clustered_row_sources: list[Any] = []

            if "quotes" in matrix_visible_cols or "criteria" in matrix_visible_cols:
                step_evals_map = {}
                for r_dto in results:
                    if r_dto.step_id == step_id and r_dto.block_id == "evaluations" and isinstance(r_dto.payload, list):
                        for ev in r_dto.payload:
                            if isinstance(ev, dict) and "tda_id" in ev:
                                step_evals_map[ev["tda_id"]] = ev
                        break

                if pb_meta.scales:
                    for scale in pb_meta.scales:
                        l_val = int(scale.score)
                        l_name = level_names[str(l_val)]
                        for claim in scale.claims:
                            claim_label = (
                                claim.label.resolve(locale)
                                if isinstance(claim.label, I18nText)
                                else str(claim.label or "")
                            )
                            for tda in claim.tda_assertions:
                                atom_id = tda.tda_id
                                ev_data = step_evals_map.get(atom_id)
                                display_label = (
                                    claim_label.strip()
                                    if claim_label.strip()
                                    else (tda.concept_description.strip() if tda.concept_description else "Kriteeri")
                                )

                                if ev_data:
                                    try:
                                        val_data = AtomResultDTO.model_validate(ev_data)

                                        r_step = ReasoningStepDTO(
                                            step_1_identify_premise="",
                                            step_2_scan_source="",
                                            step_3_evaluate_anti_patterns="",
                                            step_4_final_conclusion="",
                                        )

                                        s_atom = ScorecardAtomDTO(
                                            atom_id=atom_id,
                                            level=l_val,
                                            level_name=l_name,
                                            claim_label=claim_label,
                                            extracted_facts={},
                                            exact_quotes=[
                                                QuoteEvidenceDTO.model_validate(
                                                    {"quote": val_data.source_quote, "source_alias": []},
                                                    context={"alias_registry": {}},
                                                )
                                            ]
                                            if val_data.source_quote
                                            else [],
                                            internal_logic_en=r_step,
                                            status=val_data.status,
                                            semantic_reasoning=val_data.evaluation_reasoning or "",
                                            contextual_override=val_data.contextual_override,
                                            structural_location=None,
                                            chart_display_label=display_label,
                                            visual_intent=VisualIntent.NEUTRAL,
                                            human_override=None,
                                        )

                                    except Exception as e:
                                        logger.error(
                                            "LLM output violated strictly typed schema during Display parsing for atom %s",
                                            atom_id,
                                            exc_info=True,
                                        )
                                        raise AppException(
                                            message=f"Strict type validation failed for atom {atom_id}",
                                            status_code=500,
                                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                        ) from e

                                    evaluated_atoms_list.append(s_atom)
                                    step_scorecard_atoms.setdefault(step_id, {})[atom_id] = s_atom
                                else:
                                    dummy_reasoning = ReasoningStepDTO(
                                        step_1_identify_premise="",
                                        step_2_scan_source="",
                                        step_3_evaluate_anti_patterns="",
                                        step_4_final_conclusion="",
                                    )
                                    s_atom = ScorecardAtomDTO(
                                        atom_id=atom_id,
                                        level=l_val,
                                        level_name=l_name,
                                        claim_label=claim_label,
                                        extracted_facts={},
                                        exact_quotes=[],
                                        internal_logic_en=dummy_reasoning,
                                        status=ExecutionStatus.FAILED,
                                        semantic_reasoning="",
                                        contextual_override=False,
                                        structural_location=None,
                                        chart_display_label=display_label,
                                        visual_intent=VisualIntent.NEUTRAL,
                                        human_override=None,
                                    )
                                    evaluated_atoms_list.append(s_atom)
                                    step_scorecard_atoms.setdefault(step_id, {})[atom_id] = s_atom

            score_display_label = "-"
            if score_float is not None:
                max_val = display_scale_max if display_scale_max is not None else 100.0
                score_display_label = f"{score_float:.1f} / {max_val:.1f}"

            cleaned_explanation = MatrixDomainParser._clean_hallucinated_numbers(final_explanation)

            # Implementation Plan Phase 3, Step 1: Set inner_sdui_blocks=[]
            inner_sdui_blocks: list[AnySduiBlock] = []

            # Resolve context_target and context_target_label from StepRule input_mappings
            context_target = None
            context_target_label = None
            step_rule = workflow_steps.get(step_id)
            input_mappings = step_rule.input_mappings if step_rule else None
            if input_mappings and isinstance(input_mappings, dict):
                # Find input mapping pointing to $inputs
                for mapped_val in input_mappings.values():
                    if isinstance(mapped_val, str) and mapped_val.startswith("$inputs."):
                        context_target = mapped_val.split("$inputs.", 1)[1].strip()
                        break
                    elif isinstance(mapped_val, str) and not mapped_val.startswith("$"):
                        context_target = mapped_val.strip()
                        break

            if context_target:
                input_def = expected_inputs_map.get(context_target) if expected_inputs_map else None
                if input_def and input_def.label:
                    context_target_label = input_def.label
                else:
                    context_target_label = I18nText(translations={"fi": context_target, "en": context_target})

            remediation_steps = ext.remediation_steps if ext else None
            coaching = ext.coaching if ext else None
            falsification = ext.falsification if ext else None

            row_dto = MatrixScorecardRowDTO(
                block_id=b_id,
                name=axis_name,
                label_i18n=pb_meta.label,
                description=axis_description,
                score=score_float,
                score_display_label=score_display_label,
                scale_min=display_scale_min,
                scale_max=display_scale_max,
                normalized_score=float(norm_score) if norm_score is not None else None,
                true_atoms=true_atoms,
                total_atoms=total_atoms,
                row_explanation=cleaned_explanation,
                evidence_type=ext.evidence_type if ext else None,  # type: ignore[arg-type]
                cited_source_id=ext.source_id if ext else None,
                cited_text_quote=ext.citation if ext else None,
                cited_web_citation=ext.google_citation if ext else None,
                cited_source_title=(
                    pb_meta.theory_grounding.citation_reference
                    if pb_meta.theory_grounding and pb_meta.theory_grounding.citation_reference
                    else None
                ),
                cited_source_url=(
                    pb_meta.theory_grounding.source_url
                    if pb_meta.theory_grounding and pb_meta.theory_grounding.source_url
                    else (ext.google_citation if ext and ext.google_citation else None)
                ),
                context_target=context_target,
                context_target_label=context_target_label,
                remediation_steps=remediation_steps,
                coaching=coaching,
                falsification=falsification,
                confidence=ext.confidence if ext else None,
                contextual_override=ext.contextual_override if ext else None,
                semantic_reasoning=(
                    ext.semantic_reasoning if ext and ext.semantic_reasoning else matrix_payload.justification
                ),
                level_breakdown=axis_level_breakdown,
                level_names=level_names,
                ui_boundary_labels=ui_boundary_labels,
                ui_plot_ratio=ui_plot_ratio,
                is_evaluative=pb_meta.is_evaluative,
                allow_contextual_override=pb_meta.allow_contextual_override,
                evaluated_atoms=evaluated_atoms_list,
                clustered_row_sources=clustered_row_sources,
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

        return (
            evaluative_matrices,
            informational_matrices,
            all_parsed_matrices,
            step_scorecard_atoms,
        )
