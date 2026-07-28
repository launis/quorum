"""Blueprint Transformer Service for V3 Extreme MVC."""

import logging
import re
from typing import Any

import bleach

from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.linguistics import scan_report_for_slop
from backend_v2.models.dtos.lightweight_matrix import (
    AtomEvaluationItemDTO,
    LightweightMatrixOutput,
    MatrixEvaluationItemDTO,
    ReasoningStepDTO,
)
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO, TraceScoringPayloadDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    SystemConfigID,
    SystemLocale,
    TargetBlockType,
    VirtualSystemStepID,
    VisualIntent,
)
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import (
    EmbeddedOutputProfile,
    I18nText,
    MatrixScorecardRowDTO,
    MCPAuditTrace,
    OutputLayoutBlock,
    OutputProfile,
    PromptBlock,
    ReportDataDTO,
    ReportLayoutDTO,
    ScorecardAtomDTO,
    SystemConfigPerformativeLexicons,
)
from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
    HeroInsightBlock,
    MarkdownBlock,
    ParagraphBlock,
)
from backend_v2.settings import get_settings
from backend_v2.utils.scoring.variance_engine import calculate_mechanical_cognitive_variance

logger = logging.getLogger(__name__)


class BlueprintTransformer:
    """The Universal Transformer Hub. Parses raw execution results into ReportDataDTO."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        prompt_block_repo: IPromptBlockRepository,
        output_profile_repo: IOutputProfileRepository,
        identity_repo: IIdentityRepository,
        system_repo: ISystemRepository,
    ):
        """Initializes the BlueprintTransformer with required repository interfaces.

        Args:
            exec_repo: Repository for execution data.
            workflow_repo: Repository for workflow definitions.
            comp_repo: Repository for component definitions.
            prompt_block_repo: Repository for prompt block definitions.
            output_profile_repo: Repository for output profile definitions.
            identity_repo: Repository for identity management.
            system_repo: Repository for system configurations.
        """
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.prompt_block_repo = prompt_block_repo
        self.output_profile_repo = output_profile_repo
        self.identity_repo = identity_repo
        self.system_repo = system_repo

        from collections.abc import Callable

        self._target_block_hydrators: dict[str, Callable[..., list[AnySduiBlock]]] = {
            TargetBlockType.PENALTIES_BLOCK: self._hydrate_penalties_block,
            TargetBlockType.GLOBAL_SCORE_BLOCK: self._hydrate_global_score_block,
            TargetBlockType.AUDIT_TRAIL_BLOCK: self._hydrate_audit_trail_block,
            TargetBlockType.JARGON_RATIO_BLOCK: self._hydrate_jargon_ratio_block,
            TargetBlockType.PRINTABLE_SOURCES_BLOCK: self._hydrate_printable_sources_block,
        }

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
    def _coerce_str(val: Any) -> str | None:
        """Flattens list elements and converts mixed types to string.

        Args:
            val: Any input value.

        Returns:
            A string representation of the value, or None if the input is None.
        """
        if val is None:
            return None
        if isinstance(val, list):
            return "\n".join(str(item) for item in val if item is not None)
        if isinstance(val, (dict, set)):
            return str(val)
        return str(val).strip()

    @staticmethod
    def _coerce_float(val: Any) -> float | None:
        """Coerces percentage marks and empty strings to prevent strict float crashes.

        Args:
            val: Any numeric or string value.

        Returns:
            The float value, or None if conversion fails.
        """
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        s_val = str(val).strip()
        if not s_val:
            return None
        s_val = s_val.replace("%", "").strip()
        try:
            return float(s_val)
        except ValueError:
            logger.warning("[BlueprintTransformer] Could not coerce value '%s' to float, returning None.", val)
            return None

    @staticmethod
    def _coerce_bool(val: Any) -> bool | None:
        """Translates descriptive risk text or truthy constants into a boolean.

        Args:
            val: Any input representing a truth value.

        Returns:
            The parsed boolean value, or None if input is empty.
        """
        if val is None:
            return None
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return bool(val)
        s_val = str(val).strip().lower()
        if not s_val:
            return None
        if s_val in ("false", "no", "0", "none", "null", "undefined"):
            return False
        if s_val in ("true", "yes", "1"):
            return True
        return True

    def _apply_pii_masking(self, text: str) -> str:
        """Applies regex-based PII masking to text.

        Args:
            text: The raw text string.

        Returns:
            The redacted string.
        """
        import re

        # Basic regex fallbacks. Can be replaced with Presidio later.
        text = re.sub(r"[\w\.-]+@[\w\.-]+", "[REDACTED EMAIL]", text)
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED PHONE]", text)
        return text

    def _extract_matrices_and_extensions(
        self,
        results: list[Any],
        locale: str,
        blocks_by_id: dict[str, PromptBlock],
        workflow_steps: dict[str, Any],
        grouped_extensions: dict[str, list[Any]],
        profile: OutputProfile | EmbeddedOutputProfile,
        row_explanations_cache: dict[str, str],
        workflow_ext_values: list[str],
        row_curated_quotes_cache: dict[str, list[str]],
        has_synthesis_cache: bool = False,
        rejected_evq_ids: set[str] | None = None,
        mcp_audit_map: dict[str, MCPAuditTrace] | None = None,
        source_identity_manifest: dict[str, str] | None = None,
        execution: Any = None,
    ) -> tuple[
        list[MatrixScorecardRowDTO],
        list[MatrixScorecardRowDTO],
        dict[str, MatrixScorecardRowDTO],
        dict[str, dict[str, ScorecardAtomDTO]],
    ]:
        """Parses folded results into MatrixScorecardRowDTOs and populates grouped XAI extensions.

        Args:
            results: Folded state trace output.
            locale: Desired output locale.
            blocks_by_id: Dictionary mapping prompt block ID to its PromptBlock model.
            workflow_steps: Dictionary of step IDs to StepRule models.
            grouped_extensions: Dictionary to accumulate dynamic XAI extensions.
            profile: The resolved OutputProfile model.
            row_explanations_cache: Rendered explanations to override raw LLM justification.
            workflow_ext_values: List of requested workflow-level extension types.
            source_identity_manifest: Optional map of source ID to display names.
            execution: Optional ExecutionRecord model.

        Returns:
            A tuple of (evaluative_matrices, informational_matrices, all_parsed_matrices, step_scorecard_atoms).

        Raises:
            AppException: Triggered if strict matrix structure constraints are violated.
        """
        evaluative_matrices: list[MatrixScorecardRowDTO] = []
        informational_matrices: list[MatrixScorecardRowDTO] = []
        all_parsed_matrices: dict[str, MatrixScorecardRowDTO] = {}
        step_scorecard_atoms: dict[str, dict[str, ScorecardAtomDTO]] = {}

        # Safe attribute access using V2 Models
        display_scale = profile.display_scale
        matrix_visible_cols = ["label", "score", "distribution", "row_explanation", "quotes"]
        if profile.layouts:
            for lay in profile.layouts:
                if lay.preset_view == "3d_matrix" and lay.matrix_visible_columns:
                    matrix_visible_cols = lay.matrix_visible_columns
                    break

        for dto in results:
            step_id = dto.step_id
            b_id = dto.block_id
            block_data = dto.payload

            pb_meta = blocks_by_id.get(b_id)
            if not pb_meta or pb_meta.category_id != "matrix":
                continue

            if not isinstance(block_data, dict):
                msg = (
                    f"Strict Fail-Fast: Invalid matrix payload format for '{b_id}': "
                    f"expected dict, got {type(block_data)}"
                )
                logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

            try:
                mapped_block_data = LightweightMatrixOutput.map_llm_extensions_to_domain(block_data)
                matrix_payload = TraceMatrixPayloadDTO.model_validate(mapped_block_data)
            except Exception as e:
                msg = f"Strict Fail-Fast: Invalid matrix payload format for '{b_id}': {e}"
                logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            true_atoms = None
            total_atoms = None
            raw_score = matrix_payload.raw_score
            norm_score = matrix_payload.normalized_score

            if matrix_payload.evaluated_atoms:
                true_atoms = sum(1 for v in matrix_payload.evaluated_atoms.values() if v)
                total_atoms = len(matrix_payload.evaluated_atoms)
                if total_atoms > 0 and raw_score is None:
                    raw_score = true_atoms / total_atoms
                    norm_score = raw_score * 100.0

            axis_name = pb_meta.label.resolve(locale) if pb_meta.label else b_id
            if not axis_name:
                axis_name = b_id
            if pb_meta.is_evaluative:
                axis_name += " *"

            if not pb_meta.label:
                logger.error(
                    "[BlueprintTransformer] %s: Fail-Fast: PromptBlock '%s' is missing a required I18n label.",
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
                    "[BlueprintTransformer] %s: PromptBlock '%s' missing Pydantic computed_min/max.",
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
                    "[BlueprintTransformer] %s: PromptBlock '%s' initialized as matrix but has no scales.",
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
                        "[BlueprintTransformer] %s: Fail-Fast: MatrixScale in block '%s' missing 'name'.",
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
            if display_scale == "normalized_100":
                active_score_key = "normalized_score"
                display_scale_min = 0.0
                display_scale_max = 100.0
            elif display_scale == "custom":
                scale_min_val = pb_meta.scale_min
                scale_max_val = pb_meta.scale_max
                if scale_min_val is None or scale_max_val is None:
                    logger.error(
                        "[BlueprintTransformer] %s: UI bounds missing for PromptBlock '%s' under custom scale.",
                        ErrorCodes.CONFIGURATION_ERROR.name,
                        b_id,
                    )
                    raise AppException(
                        message=f"UI bounds missing for PromptBlock '{b_id}' under custom scale.",
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
                display_scale_min = float(scale_min_val)
                display_scale_max = float(scale_max_val)

            if active_score_key == "normalized_score":
                target_val = matrix_payload.normalized_score
            else:
                target_val = matrix_payload.raw_score

            if target_val is None:
                target_val = raw_score

            score_float = float(round(float(target_val), 1)) if target_val is not None else None
            if display_scale == "normalized_100" and score_float is not None:
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
                step_node = workflow_steps.get(step_id)
                step_title = step_id
                if step_node:
                    step_title = step_node.id
                axis_name = f"{original_axis_name} ({step_title})"
                if any(ext.name == axis_name for ext in all_parsed_matrices.values()):
                    axis_name = f"{original_axis_name} ({step_title} {collision_counter})"
                    collision_counter += 1

            axis_level_breakdown = None
            raw_breakdown = matrix_payload.level_breakdown
            if raw_breakdown and isinstance(raw_breakdown, dict):
                clean_level_dict = {}
                for lvl_key, lvl_data in raw_breakdown.items():
                    if isinstance(lvl_data, dict):
                        try:
                            f_lvl = float(lvl_key)
                            is_int = f_lvl.is_integer()
                            c_key = str(int(f_lvl)) if is_int else str(lvl_key)
                            hits = lvl_data.get("hits", 0)
                            total = lvl_data.get("total", 0)
                            clean_level_dict[c_key] = f"{hits}/{total}"
                        except ValueError as v_err:
                            logger.error(
                                "[BlueprintTransformer] %s: Fail-Fast: Invalid level key '%s' "
                                "in matrix breakdown for '%s'.",
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

            ext_dict = matrix_payload.extensions or {}

            if False:
                if b_id not in row_explanations_cache:
                    msg = f"Fail-Fast: row_explanations_cache missing entry for matrix '{b_id}'. Worker synthesis incomplete."
                    logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
                final_explanation = row_explanations_cache[b_id]
            else:
                final_explanation = row_explanations_cache.get(b_id, "")

            evaluated_atoms_list = []
            clustered_row_sources = []
            used_evidence_ids_set = set()

            if "quotes" in matrix_visible_cols:
                step_evals_map = {}
                for r_dto in results:
                    if r_dto.step_id == step_id and r_dto.block_id == "evaluations" and isinstance(r_dto.payload, list):
                        for ev in r_dto.payload:
                            if isinstance(ev, dict) and "atom_id" in ev:
                                step_evals_map[ev["atom_id"]] = ev
                        break

                if pb_meta.scales:
                    for scale in pb_meta.scales:
                        l_val = int(scale.score)
                        l_name = level_names.get(str(l_val), f"Taso {l_val}")
                        for claim in scale.claims:
                            claim_label = claim.label.resolve(locale) if isinstance(claim.label, I18nText) else "Väite"
                            for tda in claim.tda_assertions:
                                atom_id = tda.tda_id
                                ev_data = step_evals_map.get(atom_id)

                                if ev_data:
                                    is_matrix = pb_meta.category_id == "matrix"
                                    parsed_quotes = []

                                    try:
                                        if is_matrix:
                                            # Strict validation for Matrix Output
                                            val_data = MatrixEvaluationItemDTO.model_validate(ev_data)

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
                                                exact_quotes=[],
                                                internal_logic_en=r_step,
                                                status=ExecutionStatus.FAILED,
                                                semantic_reasoning=re.sub(
                                                    r"\\n\\n\[5\.\s*VALIDATION DECISION:\s*\w+\]",
                                                    "",
                                                    val_data.semantic_reasoning,
                                                ).strip(),
                                                contextual_override=False,
                                                structural_location="N/A",
                                                chart_display_label="N/A",
                                                visual_intent=VisualIntent.NEUTRAL,
                                            )
                                        else:
                                            # Strict validation for Cognitive Output
                                            val_data_cog = AtomEvaluationItemDTO.model_validate(ev_data)

                                            for qt in val_data_cog.exact_quotes:
                                                source_id = qt.source_id or "unknown"
                                                parsed_quotes.append(
                                                    QuoteEvidenceDTO(
                                                        quote=qt.text,
                                                        source_alias=[source_id],
                                                        verified_source_ids=[],
                                                        unverified_aliases=[],
                                                        is_verified=False,
                                                    )
                                                )

                                            evidence_found = (
                                                val_data_cog.status == "PASS" or val_data_cog.evidence_found
                                            )
                                            is_dlq = evidence_found is True and not parsed_quotes
                                            calc_status = (
                                                ExecutionStatus.PASSED
                                                if (evidence_found and not is_dlq)
                                                else ExecutionStatus.FAILED
                                            )

                                            s_atom = ScorecardAtomDTO(
                                                atom_id=atom_id,
                                                level=l_val,
                                                level_name=l_name,
                                                claim_label=claim_label,
                                                extracted_facts=val_data_cog.extracted_facts,
                                                exact_quotes=parsed_quotes,
                                                internal_logic_en=val_data_cog.internal_logic_en,
                                                status=calc_status,
                                                semantic_reasoning=re.sub(
                                                    r"\\n\\n\[5\.\s*VALIDATION DECISION:\s*\w+\]",
                                                    "",
                                                    val_data_cog.semantic_reasoning,
                                                ).strip(),
                                                contextual_override=val_data_cog.contextual_override,
                                                structural_location=val_data_cog.structural_location,
                                                chart_display_label=val_data_cog.chart_display_label,
                                                visual_intent=val_data_cog.visual_intent,
                                            )

                                            for u_id in val_data_cog.used_evidence_ids:
                                                used_evidence_ids_set.add(u_id)

                                    except Exception as e:
                                        # Fail-Fast requirement: Crash loudly if the model does not validate
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
                                        structural_location="N/A",
                                        chart_display_label="N/A",
                                        visual_intent=VisualIntent.NEUTRAL,
                                    )
                                    evaluated_atoms_list.append(s_atom)
                                    step_scorecard_atoms.setdefault(step_id, {})[atom_id] = s_atom

                if mcp_audit_map:
                    for uid in used_evidence_ids_set:
                        if uid in mcp_audit_map:
                            clustered_row_sources.append(mcp_audit_map[uid])

            score_display_label = "-"
            if score_float is not None:
                max_val = display_scale_max if display_scale_max is not None else 100.0
                score_display_label = f"{score_float:.1f} / {max_val:.1f}"

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
                row_explanation=self._clean_hallucinated_numbers(final_explanation),
                evidence_type=self._coerce_str(ext_dict.get("evidence_type")),  # type: ignore[arg-type]
                missing_context=self._coerce_str(ext_dict.get("missing_context")) or "",
                cited_source_id=self._coerce_str(ext_dict.get("source_id")),
                cited_text_quote=self._coerce_str(ext_dict.get("citation")),
                cited_web_citation=self._coerce_str(ext_dict.get("google_citation")),
                coaching=self._coerce_str(ext_dict.get("coaching")),
                confidence=self._coerce_float(ext_dict.get("confidence")),
                falsification=self._coerce_str(ext_dict.get("falsification")),
                risk_flag=self._coerce_bool(ext_dict.get("risk_flag")),
                remediation_steps=self._coerce_str(ext_dict.get("remediation_steps")),
                emotional_sentiment=self._coerce_str(ext_dict.get("emotional_sentiment")),
                theory_link=self._coerce_str(ext_dict.get("theory_link")),
                contextual_override=self._coerce_bool(ext_dict.get("contextual_override")),
                semantic_reasoning=(
                    self._coerce_str(ext_dict.get("semantic_reasoning"))
                    or self._coerce_str(ext_dict.get("justification"))
                ),
                level_breakdown=axis_level_breakdown,
                level_names=level_names,
                ui_boundary_labels=ui_boundary_labels,
                ui_plot_ratio=ui_plot_ratio,
                is_evaluative=pb_meta.is_evaluative,
                evaluated_atoms=evaluated_atoms_list,
                clustered_row_sources=clustered_row_sources,
                used_evidence_ids=list(used_evidence_ids_set),
            )

            unique_k = f"{step_id}_{b_id}"
            all_parsed_matrices[unique_k] = row_dto

            for ext_key, ext_val in ext_dict.items():
                if ext_val and ext_key in grouped_extensions:
                    # Curation of Matrix Extensions, Step 3: Skip raw step-level extensions if curated synthesis exists/has run
                    if has_synthesis_cache:
                        continue
                    if any(item.get("_is_synthesized") for item in grouped_extensions[ext_key]):
                        continue
                    grouped_extensions[ext_key].append(
                        {
                            "axis_name": axis_name,
                            ext_key: ext_val,
                            "_score": score_float,
                        }
                    )

            if pb_meta.is_evaluative:
                evaluative_matrices.append(row_dto)
            else:
                informational_matrices.append(row_dto)

        # Sort and limit extensions
        max_items = profile.max_extension_items
        if max_items is not None and max_items > 0:
            for ext_key in grouped_extensions:
                if ext_key in workflow_ext_values:
                    continue
                synthesized = [x for x in grouped_extensions[ext_key] if x.get("_is_synthesized")]
                raw_items = [x for x in grouped_extensions[ext_key] if not x.get("_is_synthesized")]
                combined = synthesized + raw_items
                grouped_extensions[ext_key] = combined[:max_items]

        return evaluative_matrices, informational_matrices, all_parsed_matrices, step_scorecard_atoms

    def _hydrate_penalties_block(self, **kwargs: Any) -> list[AnySduiBlock]:
        """Hydrates penalty visual blocks with CRITICAL_OVERRIDE intent."""
        penalties_applied: list[str] = kwargs.get("penalties_applied", [])
        if not penalties_applied:
            return []

        penalty_blocks: list[AnySduiBlock] = []
        for p_str in penalties_applied:
            penalty_blocks.append(
                AlertBlock(
                    severity=VisualIntent.CRITICAL_OVERRIDE.value,
                    text=f"Penalty applied: {p_str}",
                    exact_quotes=[],
                    citations=[],
                )
            )
        return penalty_blocks

    def _hydrate_global_score_block(self, **kwargs: Any) -> list[AnySduiBlock]:
        """Placeholder for future global score hydration logic."""
        return []

    def _hydrate_audit_trail_block(self, **kwargs: Any) -> list[AnySduiBlock]:
        """Placeholder for future audit trail hydration logic."""
        return []

    def _hydrate_jargon_ratio_block(self, **kwargs: Any) -> list[AnySduiBlock]:
        """Placeholder for future jargon ratio hydration logic."""
        return []

    def _hydrate_printable_sources_block(self, **kwargs: Any) -> list[AnySduiBlock]:
        """Placeholder for future printable sources hydration logic."""
        return []

    def _build_layouts(
        self,
        layout_defs: list[OutputLayoutBlock],
        all_parsed_matrices: dict[str, MatrixScorecardRowDTO],
        section_syntheses: dict[str, list[AnySduiBlock]],
    ) -> list[ReportLayoutDTO]:
        """Maps generated axes into report layouts based on layout rules.

        Args:
            layout_defs: List of layout block definitions.
            all_parsed_matrices: Dictionary of all resolved MatrixScorecardRowDTOs.
            section_syntheses: Mappings of layout ID to its synthesis markdown.

        Returns:
            List of completely rendered ReportLayoutDTOs.

        Raises:
            AppException: If layout validation (e.g. 3d minimums) fails.
        """
        layouts_list: list[ReportLayoutDTO] = []
        for idx, layout_def in enumerate(layout_defs):
            preset_view = layout_def.preset_view
            target_blocks = layout_def.target_blocks
            text_delivery_mode = layout_def.text_delivery_mode

            layout_title = layout_def.title
            layout_desc = layout_def.description

            axes = []
            if target_blocks and "*" not in target_blocks:
                for target_k in target_blocks:
                    matched = next((axis for axis in all_parsed_matrices.values() if axis.block_id == target_k), None)
                    if matched:
                        axes.append(matched)
            else:
                axes = list(all_parsed_matrices.values())

            if preset_view in ["3d_complex", "3d_matrix"] and len(axes) < 3:
                logger.warning(
                    "[BlueprintTransformer] Downgrading layout '%s' from %s to 2d_compare because only %s axes found.",
                    layout_title,
                    preset_view,
                    len(axes),
                )
                preset_view = "2d_compare"

            if preset_view == "2d_compare" and len(axes) < 2:
                logger.warning(
                    "[BlueprintTransformer] Downgrading layout '%s' from 2d_compare to "
                    "1d_metrics because only %s axes found.",
                    layout_title,
                    len(axes),
                )
                preset_view = "1d_metrics"

            if axes or preset_view == "text_only" or layout_def.synthesis:
                synthesis_config = layout_def.synthesis
                layout_id = f"layout_{idx}_{preset_view}"

                section_blocks = None
                if synthesis_config:
                    if layout_id in section_syntheses:
                        section_blocks = section_syntheses[layout_id]

                layouts_list.append(
                    ReportLayoutDTO(
                        preset_view=preset_view,
                        title=layout_title,
                        description=layout_desc,
                        is_synthesis_enabled=layout_def.is_synthesis_enabled,
                        axes=axes,
                        target_blocks=target_blocks,
                        text_delivery_mode=text_delivery_mode,
                        synthesis=synthesis_config,
                        synthesis_blocks=section_blocks,
                        matrix_column_labels=layout_def.matrix_column_labels,
                        extension_labels=layout_def.extension_labels,
                    )
                )
        if not layouts_list and all_parsed_matrices:
            layouts_list.append(
                ReportLayoutDTO(
                    preset_view="default",
                    axes=list(all_parsed_matrices.values()),
                )
            )

        return layouts_list

    async def build_report_dto(
        self,
        execution_id: str,
        profile_id: str | None = None,
        accept_language: str | None = None,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> ReportDataDTO:
        """Builds the strictly typed report payload by parsing results according to the selected profile.

        Args:
            execution_id: Identifier of the execution.
            profile_id: Optional Output Profile ID to override the workflow default.
            accept_language: Optional locale string for localized titles.
            custom_preface_md: Optional custom markdown preface string.
            local_time_str: Optional formatted string representing local time of generation.

        Returns:
            A strictly typed ReportDataDTO containing the synthesized execution report.

        Raises:
            AppException: Triggered for RESOURCE_NOT_FOUND, VALIDATION_FAILED, or CONFIGURATION_ERROR.
        """
        execution = await self.exec_repo.get_execution(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        workflow_obj = await self.workflow_repo.get_workflow(execution.workflow_id)
        if not workflow_obj:
            msg = f"Executing workflow {execution.workflow_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        projector = StateProjector()
        results = projector.fold_trace(execution.execution_trace)

        locale = accept_language or (
            execution.metadata.get("target_locale", SystemLocale.EN.value)
            if isinstance(execution.metadata, dict)
            else SystemLocale.EN.value
        )

        default_profile_ref = workflow_obj.default_profile_id
        resolved_pid_request = profile_id if profile_id and profile_id != "default" else default_profile_ref

        all_profiles_dicts = await self.output_profile_repo.get_all_output_profiles()
        all_profiles = [OutputProfile.model_validate(p_dict, strict=False) for p_dict in all_profiles_dicts]

        profile = next((p for p in all_profiles if p.id == resolved_pid_request), None)

        if not profile:
            msg = f"Output profile '{resolved_pid_request}' not found in the database. Failing fast."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        resolved_pid = str(profile.id)

        available_profiles_map = {p.id: p.name for p in all_profiles}
        if resolved_pid not in available_profiles_map:
            available_profiles_map[resolved_pid] = profile.name

        profile_name_dict = profile.name

        block_ext_values = (
            [v.value for v in profile.visible_block_extensions] if profile.visible_block_extensions else []
        )
        workflow_ext_values = (
            [v.value for v in profile.visible_workflow_extensions] if profile.visible_workflow_extensions else []
        )
        grouped_extensions: dict[str, list[Any]] = {
            ext: [] for ext in block_ext_values + workflow_ext_values if ext != "source_id"
        }

        all_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()
        blocks_by_id: dict[str, PromptBlock] = {}
        for b_dict in all_blocks_raw:
            b = PromptBlock.model_validate(b_dict, strict=False)
            if b.id:
                blocks_by_id[b.id] = b

        has_warning = False
        synthesis_md = None
        scoring_out = None

        synthesis_block_id = None

        for dto in results:
            if dto.block_id == VirtualSystemStepID.SCORING_RESULT.value and isinstance(dto.payload, dict):
                scoring_out = dto.payload
            if dto.block_id == VirtualSystemStepID.HAS_WARNING.value and dto.payload:
                has_warning = True
            if dto.block_id == VirtualSystemStepID.SYNTHESIZED_MARKDOWN.value and dto.payload:
                synthesis_md = dto.payload

            # Epic 94: Polymorphic dynamic block mapping
            if synthesis_block_id and isinstance(dto.payload, dict) and synthesis_block_id in dto.payload:
                synthesis_md = dto.payload[synthesis_block_id]

        profile_cache = execution.profile_syntheses.get(resolved_pid)
        original_synthesis_md = synthesis_md
        section_syntheses: dict[str, list[AnySduiBlock]] = {}
        xai_highlights_cache: list[Any] = []
        content_blocks: list[AnySduiBlock] = (
            [b.model_copy(deep=True) for b in profile.content_blocks] if profile.content_blocks else []
        )

        if profile_cache:
            section_syntheses = profile_cache.section_syntheses or {}
            # Epic 94: Do NOT overwrite profile.content_blocks with cached synthesis blocks!
            # The OutputProfile is the Single Source of Truth for SDUI layout.
            if not content_blocks and profile_cache.content_blocks:
                content_blocks = [b.model_copy(deep=True) for b in profile_cache.content_blocks]
            synthesis_md = profile_cache.synthesized_markdown or original_synthesis_md
            xai_highlights_cache = profile_cache.xai_highlights or []
        else:
            synthesis_md = original_synthesis_md

        for highlight in xai_highlights_cache:
            t_name = highlight.extension_type
            if not t_name:
                logger.error(
                    "[BlueprintTransformer] %s: Fail-Fast: Cached XaiHighlightItem missing 'extension_type'.",
                    ErrorCodes.VALIDATION_FAILED.name,
                )
                raise AppException(
                    message="Fail-Fast: Cached XaiHighlightItem missing 'extension_type'.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            group_key = t_name.lower().replace(" ", "_")
            grouped_extensions.setdefault(group_key, [])
            grouped_extensions[group_key].append(
                {group_key: highlight.content, "content": highlight.content, "_score": -999.0, "_is_synthesized": True}
            )

        report_context_dict = execution.context_variables.get("report_context")
        if isinstance(report_context_dict, dict):
            output_exts = report_context_dict.get("output_extensions", [])
            if isinstance(output_exts, list):
                for ext in output_exts:
                    if isinstance(ext, dict) and ext.get("extension_type") in workflow_ext_values:
                        e_type = ext.get("extension_type")
                        if e_type in grouped_extensions:
                            ext_copy = ext.copy()
                            ext_copy["_is_synthesized"] = True
                            grouped_extensions[e_type].append(ext_copy)

        for wf_ext in workflow_ext_values:
            if wf_ext == "variance_validation" and wf_ext in grouped_extensions and not grouped_extensions[wf_ext]:
                authenticity_score = None
                performative_phrases_count = None

                cv = execution.context_variables or {}

                # Retrieve authenticity score from step_detector payload in context_variables
                step_det = cv.get("step_detector")
                if step_det is not None:
                    from pydantic import ValidationError

                    from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput

                    try:
                        det_out = LightweightMatrixOutput.model_validate(step_det, strict=False)
                        if det_out.raw_score is not None:
                            authenticity_score = float(det_out.raw_score)
                    except ValidationError as ve:
                        logger.warning(
                            "[BlueprintTransformer] Non-fatal schema mismatch in step_detector payload: %s", ve
                        )

                if authenticity_score is None:
                    # Dynamically resolve authenticity score from the performativity detector step in the folded trace
                    performativity_step_ids = {
                        step.id for step in workflow_obj.steps if step.task_blueprint == "sp_7f9649114d2344dc"
                    }
                    for result_dto in results:
                        if result_dto.step_id in performativity_step_ids:
                            payload = result_dto.payload
                            if isinstance(payload, dict) and "raw_score" in payload:
                                raw_val = payload.get("raw_score")
                                if raw_val is not None:
                                    block = blocks_by_id.get(result_dto.block_id)
                                    if block and block.computed_min is not None and block.computed_max is not None:
                                        math_min = float(block.computed_min)
                                        math_max = float(block.computed_max)
                                        if math_max > math_min:
                                            # Scale the authenticity score from [math_min, math_max] to the [1.0, 3.0] scale
                                            authenticity_score = (
                                                (float(raw_val) - math_min) / (math_max - math_min)
                                            ) * 2.0 + 1.0
                                            break
                                        else:
                                            msg_bounds = f"PromptBlock '{result_dto.block_id}' has invalid math boundaries: math_min={math_min}, math_max={math_max}"
                                            logger.error(
                                                "[BlueprintTransformer] %s: %s",
                                                ErrorCodes.VALIDATION_FAILED.name,
                                                msg_bounds,
                                            )
                                            raise AppException(
                                                message=msg_bounds,
                                                status_code=500,
                                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                            )
                                    else:
                                        msg_missing = f"PromptBlock '{result_dto.block_id}' computed bounds are missing or block not found."
                                        logger.error(
                                            "[BlueprintTransformer] %s: %s",
                                            ErrorCodes.VALIDATION_FAILED.name,
                                            msg_missing,
                                        )
                                        raise AppException(
                                            message=msg_missing,
                                            status_code=500,
                                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                        )

                # Retrieve performative phrases count from step_linguistics payload in context_variables
                step_ling = cv.get("step_linguistics")
                if step_ling is not None:
                    from pydantic import ValidationError

                    from backend_v2.models.domain.linguistics import LinguisticsResultDTO

                    try:
                        ling_out = LinguisticsResultDTO.model_validate(step_ling, strict=False)
                        patterns = ling_out.performative_patterns
                        if isinstance(patterns, list):
                            performative_phrases_count = len(patterns)
                    except ValidationError as ve:
                        logger.warning(
                            "[BlueprintTransformer] Non-fatal schema mismatch in step_linguistics payload: %s", ve
                        )

                if performative_phrases_count is None:
                    # Dynamically resolve linguistics performative patterns count from decision events in execution trace
                    for event in reversed(execution.execution_trace):
                        if event.event_type == "decision" and "step_linguistics" in event.content:
                            trace_ling = event.content.get("step_linguistics")
                            if isinstance(trace_ling, dict) and "performative_patterns" in trace_ling:
                                trace_patterns = trace_ling.get("performative_patterns")
                                if isinstance(trace_patterns, list):
                                    performative_phrases_count = len(trace_patterns)
                                    break

                if authenticity_score is None or performative_phrases_count is None:
                    msg = (
                        "Strict Fail-Fast Enforced: 'variance_validation' requested but authenticity_score "
                        f"({authenticity_score}) or performative_phrases_count ({performative_phrases_count}) is missing."
                    )
                    logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

                variance_res = calculate_mechanical_cognitive_variance(
                    llm_authenticity_score=authenticity_score,
                    performative_phrases_count=performative_phrases_count,
                )

                dynamic_ext = {
                    "extension_type": "variance_validation",
                    "mechanical_metric_ref": "performative_phrases_count",
                    "cognitive_metric_ref": "llm_authenticity_score",
                    "variance_score": float(variance_res["variance_score"]),
                    "alignment_verdict": str(variance_res["alignment_verdict"]),
                    "_is_synthesized": True,
                }
                grouped_extensions[wf_ext].append(dynamic_ext)

        if any(dto.block_id == VirtualSystemStepID.HAS_WARNING.value and dto.payload for dto in results):
            has_warning = True

        global_score = None
        penalties_applied: list[str] = []
        if isinstance(scoring_out, dict):
            try:
                score_dto = TraceScoringPayloadDTO.model_validate(scoring_out)
                t_score = score_dto.total_score
                global_score = float(round(float(t_score), 1)) if t_score is not None else None
                raw_penalties = score_dto.penalties_applied
                if isinstance(raw_penalties, list):
                    for p in raw_penalties:
                        p_str = str(p)
                        if p_str.startswith("PENALTY_SECURITY:") or p_str.startswith("PENALTY_POST_HOC:"):
                            penalties_applied.append(p_str)
                        else:
                            # Enforce Zero-Compromise Check: fail fast on legacy/unsupported penalty format
                            msg_legacy = f"Zero-Compromise Check Failed: Legacy or unsupported penalty string detected: '{p_str}'"
                            logger.error("[BlueprintTransformer] %s", msg_legacy)
                            raise AppException(
                                message=msg_legacy,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
            except Exception as e:
                logger.error(
                    "[BlueprintTransformer] %s: Scoring payload extraction failed: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Scoring payload extraction failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        # Epic 88 Phase 6: Pass rejected_evq_ids to the matrix extractor
        rejected_evq_ids: set[str] = set()
        if execution.execution_trace:
            for ev in execution.execution_trace:
                if ev.event_type == "evidence_override" and isinstance(ev.content, dict):
                    if ev.content.get("user_rejected") is True:
                        evq_id = ev.content.get("evq_id")
                        if isinstance(evq_id, str):
                            rejected_evq_ids.add(evq_id)

        mcp_audit_map: dict[str, MCPAuditTrace] = {}
        if execution.frozen_context and execution.frozen_context.mcp_tool_audit:
            for trace in execution.frozen_context.mcp_tool_audit:
                if trace.id:
                    mcp_audit_map[trace.id] = trace

        v2_results: list[Any] = []
        v2_hydrated_refs: dict[str, Any] = {}

        from backend_v2.models.v2_core import AtomResultDTO, HydratedAtomDTO

        for dto in results:
            if isinstance(dto.payload, dict):
                if "results" in dto.payload and isinstance(dto.payload["results"], list):
                    for r_dict in dto.payload["results"]:
                        v2_results.append(AtomResultDTO.model_validate(r_dict))
                if "hydrated_references" in dto.payload and dto.payload["hydrated_references"]:
                    for k, v_dict in dto.payload["hydrated_references"].items():
                        v2_hydrated_refs[k] = HydratedAtomDTO.model_validate(v_dict)

        workflow_steps_map = {s.id: s for s in workflow_obj.steps} if workflow_obj.steps else {}
        row_explanations_cache: dict[str, str] = {}
        row_curated_quotes_cache: dict[str, list[str]] = {}

        if profile_cache and profile_cache.row_explanations:
            row_explanations_cache = profile_cache.row_explanations
        if profile_cache and profile_cache.row_curated_quotes:
            row_curated_quotes_cache = profile_cache.row_curated_quotes

        evaluative_matrices, informational_matrices, all_parsed_matrices, step_scorecard_atoms = (
            self._extract_matrices_and_extensions(
                results=results,
                locale=locale,
                blocks_by_id=blocks_by_id,
                workflow_steps=workflow_steps_map,
                grouped_extensions=grouped_extensions,
                profile=profile,
                row_explanations_cache=row_explanations_cache,
                workflow_ext_values=workflow_ext_values,
                row_curated_quotes_cache=row_curated_quotes_cache,
                has_synthesis_cache=bool(profile_cache),
                rejected_evq_ids=rejected_evq_ids,
                mcp_audit_map=mcp_audit_map,
                source_identity_manifest=None,
                execution=execution,
            )
        )

        modified_step_states = False
        new_step_states = dict(execution.step_states)
        for step_id, atoms_dict in step_scorecard_atoms.items():
            if step_id in new_step_states:
                updated_atoms = {}
                for atom_id, s_atom in atoms_dict.items():
                    existing_atom = new_step_states[step_id].scorecard_atoms.get(atom_id)
                    if existing_atom and existing_atom.human_override:
                        s_atom = s_atom.model_copy(update={"human_override": existing_atom.human_override})
                    updated_atoms[atom_id] = s_atom

                new_step_states[step_id] = new_step_states[step_id].model_copy(
                    update={"scorecard_atoms": updated_atoms}
                )
                modified_step_states = True

        if modified_step_states:
            execution = execution.model_copy(update={"step_states": new_step_states})
            await self.exec_repo.update_execution(
                execution.id, {"step_states": {k: v.model_dump(mode="json") for k, v in new_step_states.items()}}
            )

        try:
            layouts_list = self._build_layouts(profile.layouts, all_parsed_matrices, section_syntheses)

            injected = False
            if synthesis_block_id and content_blocks:
                new_content_blocks: list[AnySduiBlock] = []
                for c_block in content_blocks:
                    if c_block.id == synthesis_block_id:
                        if profile_cache and profile_cache.content_blocks and not synthesis_md:
                            # Epic 94: SDUI Block Splicing
                            for cache_b in profile_cache.content_blocks:
                                new_content_blocks.append(cache_b.model_copy(deep=True))
                            injected = True
                        elif synthesis_md:
                            # Legacy Markdown Fallback
                            allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
                                "h1",
                                "h2",
                                "h3",
                                "h4",
                                "h5",
                                "h6",
                                "p",
                                "br",
                                "hr",
                                "strong",
                                "em",
                                "u",
                                "b",
                                "i",
                                "ul",
                                "ol",
                                "li",
                                "a",
                                "span",
                                "div",
                                "pre",
                                "code",
                                "blockquote",
                                "table",
                                "thead",
                                "tbody",
                                "tr",
                                "th",
                                "td",
                            ]
                            allowed_attributes = {"*": ["class", "id"], "a": ["href", "title", "target"]}
                            safe_md = bleach.clean(
                                str(synthesis_md), tags=allowed_tags, attributes=allowed_attributes, strip=True
                            ).strip()
                            if not safe_md:
                                safe_md = "-"
                            updated_c_block = c_block.model_copy(update={"text": safe_md})
                            new_content_blocks.append(updated_c_block)
                            injected = True
                        else:
                            # Epic 94 fix: If there is no synthesis_md and no cache, keep the original block
                            # to maintain exact schema parity for Flutter and PDF renders.
                            logger.debug(
                                "[BlueprintTransformer] SDUI Block Splicing fallback triggered for '%s'. Missing synthesis_md.",
                                synthesis_block_id,
                            )
                            new_content_blocks.append(c_block)
                            injected = True
                    else:
                        new_content_blocks.append(c_block)

                if injected:
                    content_blocks = new_content_blocks

            synthesis_cfg = None
            if profile.layouts:
                for lay in profile.layouts:
                    if lay.synthesis:
                        synthesis_cfg = lay.synthesis
                        break

            if synthesis_cfg and synthesis_cfg.preamble_text:
                from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

                compiler = PromptCompiler()
                resolved_preamble = compiler.resolve_i18n(synthesis_cfg.preamble_text, locale)
                if resolved_preamble:
                    content_blocks.insert(0, MarkdownBlock(id="preamble", text=resolved_preamble))

            if synthesis_cfg and synthesis_cfg.enable_pii_masking:
                for idx, cb in enumerate(content_blocks):
                    if isinstance(cb, (MarkdownBlock, ParagraphBlock, AlertBlock, HeroInsightBlock)):
                        content_blocks[idx] = cb.model_copy(update={"text": self._apply_pii_masking(cb.text)})
                for _layout_id, sec_blocks in section_syntheses.items():
                    for idx, sb in enumerate(sec_blocks):
                        if isinstance(sb, (MarkdownBlock, ParagraphBlock, AlertBlock, HeroInsightBlock)):
                            sec_blocks[idx] = sb.model_copy(update={"text": self._apply_pii_masking(sb.text)})

            if not injected and synthesis_block_id and profile.content_blocks:
                msg = f"Synthesis mapping failed: No SDUI ContentBlock found with id '{synthesis_block_id}' in OutputProfile. Fallback is forbidden."
                logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )
        except AppException:
            raise
        except Exception as e:
            msg = f"Failed to build layout DTO: {e}"
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        org_name = execution.organization_id
        if execution.organization_id:
            try:
                org = await self.identity_repo.get_organization_model(execution.organization_id)
                if org:
                    org_name = org.name
            except Exception as org_err:
                logger.error(
                    "[BlueprintTransformer] RESOURCE_NOT_FOUND: Failed to resolve org name "
                    f"for id {execution.organization_id}: {org_err}",
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to resolve org name for id {execution.organization_id}",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                ) from org_err

        user_name = None
        if execution.created_by:
            try:
                user_dict = await self.identity_repo.get_user(execution.created_by)
                if user_dict and "name" in user_dict:
                    user_name = user_dict["name"]
                elif user_dict and "display_name" in user_dict:
                    user_name = user_dict["display_name"]
            except Exception as u_err:
                msg_err = f"Failed to resolve user name for id {execution.created_by}"
                logger.error(
                    "[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg_err, exc_info=True
                )
                raise AppException(
                    message=msg_err,
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                ) from u_err

        s_strat = workflow_obj.default_scoring_strategy.value
        if profile.scoring_strategy is not None:
            s_strat = profile.scoring_strategy.value

        engine_str = str(s_strat)

        try:
            p_tokens = 0
            c_tokens = 0
            r_tokens = 0
            t_tokens = 0
            cost = 0.0

            if execution.execution_trace:
                for dto in results:
                    if dto.block_id == VirtualSystemStepID.STEP_METADATA.value and isinstance(dto.payload, dict):
                        usage = dto.payload.get("token_usage")
                        if isinstance(usage, dict):
                            p_tokens += int(usage.get("prompt_tokens") or 0)
                            c_tokens += int(usage.get("completion_tokens") or 0)
                            r_tokens += int(usage.get("reasoning_tokens") or 0)
                            t_tokens += int(usage.get("total_tokens") or 0)
                            cost += float(usage.get("cost_usd") or 0.0)

            if t_tokens == 0 and execution.execution_trace:
                logger.warning("[BlueprintTransformer] ALARM: 0 tokens for %s. Telemetry missing.", execution.id)

            if not layouts_list:
                logger.warning(
                    "[BlueprintTransformer] ALARM: 0 Layouts generated for execution %s. UI will render empty.",
                    execution.id,
                )

            mcp_audit_data: list[MCPAuditTrace] = []
            if execution.frozen_context and execution.frozen_context.mcp_tool_audit:
                raw_audits: list[MCPAuditTrace] = execution.frozen_context.mcp_tool_audit
                seen_audits: set[str] = set()
                for audit in raw_audits:
                    if audit.tool_id == "internal_source":
                        continue

                    audit_hash = f"{audit.tool_id}::{audit.query}"
                    if audit_hash not in seen_audits:
                        seen_audits.add(audit_hash)
                        mcp_audit_data.append(audit)

            # Phase 2.3: Reverse Lookup Mapping for MCP Audit Traces
            if mcp_audit_data:
                evidence_to_axes: dict[str, set[str]] = {}

                def extract_evidence_ids(payload_data: Any, b_id: str) -> None:
                    if isinstance(payload_data, dict):
                        if "source_id" in payload_data and isinstance(payload_data["source_id"], str):
                            evidence_to_axes.setdefault(payload_data["source_id"], set()).add(b_id)
                        if "used_evidence_ids" in payload_data and isinstance(payload_data["used_evidence_ids"], list):
                            for e_id in payload_data["used_evidence_ids"]:
                                if isinstance(e_id, str):
                                    evidence_to_axes.setdefault(e_id, set()).add(b_id)
                        if "used_mcp_ids" in payload_data and isinstance(payload_data["used_mcp_ids"], list):
                            for e_id in payload_data["used_mcp_ids"]:
                                if isinstance(e_id, str):
                                    evidence_to_axes.setdefault(e_id, set()).add(b_id)
                        for val in payload_data.values():
                            extract_evidence_ids(val, b_id)
                    elif isinstance(payload_data, list):
                        for item in payload_data:
                            extract_evidence_ids(item, b_id)

                for dto in results:
                    extract_evidence_ids(dto.payload, dto.block_id)

                block_to_axis = {matrix_row.block_id: matrix_row.name for matrix_row in all_parsed_matrices.values()}

                for idx, audit in enumerate(mcp_audit_data):
                    if audit.id in evidence_to_axes:
                        axis_names = set()
                        for block_id in evidence_to_axes[audit.id]:
                            if block_id in block_to_axis:
                                axis_names.add(block_to_axis[block_id])
                        mcp_audit_data[idx] = audit.model_copy(update={"impacted_axis_names": sorted(list(axis_names))})

            strictness_level = (
                profile.strictness_level
                if profile.strictness_level is not None
                else workflow_obj.default_strictness_level
            )
            scoring_strategy = (
                profile.scoring_strategy
                if profile.scoring_strategy is not None
                else workflow_obj.default_scoring_strategy
            ).value

            resolved_preface_md = custom_preface_md
            if profile.custom_preface:
                resolved_preface_md = profile.custom_preface.resolve(locale)

                content_blocks.insert(0, MarkdownBlock(id="preface_md", text=resolved_preface_md))

            if content_blocks:
                target_layout = next((lay for lay in layouts_list if lay.is_synthesis_enabled), None)
                if not target_layout and layouts_list:
                    target_layout = layouts_list[0]

                if target_layout:
                    new_blocks = content_blocks
                    if target_layout.synthesis_blocks:
                        new_blocks = content_blocks + target_layout.synthesis_blocks
                    idx = layouts_list.index(target_layout)
                    layouts_list[idx] = target_layout.model_copy(update={"synthesis_blocks": new_blocks})

            visible_metadata = profile.visible_metadata if profile.visible_metadata else []

            # Run dynamic performative AI jargon (slop) scanning if enabled
            should_scan_slop = any(
                bool(inp.scan_for_performative_patterns) for inp in (workflow_obj.expected_inputs or [])
            )

            if should_scan_slop:
                lang = locale or "en"
                # Fetch system config using proper SystemRepository
                config_data = await self.system_repo.get_system_config(SystemConfigID.PERFORMATIVE_LEXICONS.value)
                if not config_data:
                    msg_cfg = f"Fail-Fast: Performative Lexicon config '{SystemConfigID.PERFORMATIVE_LEXICONS.value}' missing from database."
                    logger.error("[BlueprintTransformer] %s", msg_cfg)
                    raise AppException(
                        message=msg_cfg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                config_obj = SystemConfigPerformativeLexicons.model_validate(config_data)
                target_lexicon = config_obj.lexicon_configs.get(lang)
                if not target_lexicon or not target_lexicon.words:
                    msg_lex = f"Fail-Fast: Missing performative lexicon words for language '{lang}'."
                    logger.error("[BlueprintTransformer] %s", msg_lex)
                    raise AppException(
                        message=msg_lex,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

                lexicon = target_lexicon.words
                fuzz_threshold = target_lexicon.fuzz_threshold

            global_synth = None
            if profile_cache and any(v is not None for v in (profile_cache.user_role, profile_cache.executive_summary)):
                from backend_v2.models.v2_core import GlobalSynthesisDTO

                global_synth = GlobalSynthesisDTO(
                    executive_summary=profile_cache.executive_summary or "Executive summary.",
                    urgency_level=profile_cache.urgency_level or 1,
                    user_role=profile_cache.user_role or "Yleinen yleisö",
                    user_role_justification=profile_cache.user_role_justification or "Inferred from general context.",
                )
            else:
                for md_source in [synthesis_md, original_synthesis_md]:
                    if isinstance(md_source, dict):
                        user_role_val = md_source.get("user_role") or "Yleinen yleisö"
                        user_role_just = md_source.get("user_role_justification") or "Inferred from general context."
                        exec_summary = md_source.get("executive_summary") or "Executive summary."
                        urgency = md_source.get("urgency_level") or 1

                        if any(v is not None for v in (user_role_val, user_role_just, exec_summary, urgency)):
                            from backend_v2.models.v2_core import GlobalSynthesisDTO

                            global_synth = GlobalSynthesisDTO(
                                executive_summary=exec_summary,
                                urgency_level=urgency,
                                user_role=user_role_val,
                                user_role_justification=user_role_just,
                            )
                            break

            if profile.user_role_label and (not global_synth or not global_synth.user_role):
                msg = (
                    "Fail-Fast: OutputProfile requires a user_role_label but LLM synthesis failed to extract user_role."
                )
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

            if should_scan_slop:
                # Build a temporary ReportDataDTO for the slop scanner
                temp_dto = ReportDataDTO(
                    strictness_level=strictness_level,
                    scoring_strategy=scoring_strategy,
                    scoring_engine_name=engine_str,
                    user_name=user_name,
                    workflow_id=execution.workflow_id,
                    execution_id=execution_id,
                    profile_id=resolved_pid,
                    profile_name=profile_name_dict,
                    profile_description=profile.description,
                    available_profiles=available_profiles_map,
                    created_at=execution.created_at,
                    local_time_str=local_time_str,
                    custom_preface_md=resolved_preface_md,
                    org_name=org_name,
                    global_score=0.0,
                    has_warning=has_warning,
                    visible_metadata=visible_metadata,
                    layouts=layouts_list,
                    cost_estimate=cost,
                    total_tokens=t_tokens,
                    prompt_tokens=p_tokens,
                    completion_tokens=c_tokens,
                    reasoning_tokens=r_tokens,
                    mcp_tool_audit=mcp_audit_data,
                    grouped_extensions=grouped_extensions,
                    results=v2_results,
                    hydrated_references=v2_hydrated_refs,
                    global_synthesis=global_synth,
                )
                slop_phrases = scan_report_for_slop(temp_dto, lexicon, fuzz_threshold)

                if len(slop_phrases) >= get_settings().slop_phrase_warning_threshold:
                    logger.warning(
                        "[BlueprintTransformer] OutputQualityScanner detected slop for %s: %s",
                        execution.id,
                        slop_phrases,
                    )
                    has_warning = True
                    phrases_str = ",".join(slop_phrases)
                    penalties_applied.append(f"PENALTY_SLOP:{phrases_str}")

            if evaluative_matrices:
                total_norm = sum(m.normalized_score for m in evaluative_matrices if m.normalized_score is not None)
                count_norm = sum(1 for m in evaluative_matrices if m.normalized_score is not None)
                if count_norm > 0:
                    base_avg = total_norm / count_norm

                    effective_penalty = 0.0
                    for penalty_str in penalties_applied:
                        if penalty_str.startswith("PENALTY_SECURITY:"):
                            pct = float(penalty_str.split(":")[1])
                            effective_penalty += pct / 100.0
                        elif penalty_str.startswith("PENALTY_POST_HOC:"):
                            pct = float(penalty_str.split(":")[1])
                            effective_penalty += pct / 100.0
                        elif penalty_str.startswith("PENALTY_SLOP:"):
                            effective_penalty += 0.05
                        else:
                            # Enforce Zero-Compromise Check: fail fast on legacy/unsupported penalty format
                            msg_fmt = (
                                f"Zero-Compromise Check Failed: Unsupported or legacy penalty format: '{penalty_str}'"
                            )
                            logger.error("[BlueprintTransformer] %s", msg_fmt)
                            raise AppException(
                                message=msg_fmt,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                    effective_penalty = min(effective_penalty, 0.40)
                    recalc_final = base_avg * (1.0 - effective_penalty)
                    global_score = float(round(max(0.0, recalc_final), 1))

            # Phase 2: Post-process explicit layout target blocks via Strategy Pattern
            for layout in layouts_list:
                if layout.target_blocks and "*" not in layout.target_blocks:
                    new_synthesis_blocks = list(layout.synthesis_blocks) if layout.synthesis_blocks else []
                    modified_blocks = False
                    for target_k in layout.target_blocks:
                        if target_k in self._target_block_hydrators:
                            hydrated_blocks = self._target_block_hydrators[str(target_k)](
                                execution=execution,
                                locale=locale,
                                penalties_applied=penalties_applied,
                                mcp_audit_data=mcp_audit_data,
                                global_score=global_score,
                            )
                            if hydrated_blocks:
                                new_synthesis_blocks.extend(hydrated_blocks)
                                modified_blocks = True
                        elif target_k in [e.value for e in TargetBlockType]:
                            msg_fmt = f"Fail-Fast: Hydrator missing for TargetBlockType '{target_k}'"
                            logger.error("[BlueprintTransformer] %s", msg_fmt)
                            raise AppException(
                                message=msg_fmt,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                    if modified_blocks:
                        idx = layouts_list.index(layout)
                        layouts_list[idx] = layout.model_copy(update={"synthesis_blocks": new_synthesis_blocks})

            report_dto = ReportDataDTO(
                strictness_level=strictness_level,
                scoring_strategy=scoring_strategy,
                scoring_engine_name=engine_str,
                user_name=user_name,
                workflow_id=execution.workflow_id,
                execution_id=execution_id,
                profile_id=resolved_pid,
                profile_name=profile_name_dict,
                profile_description=profile.description,
                available_profiles=available_profiles_map,
                created_at=execution.created_at,
                local_time_str=local_time_str,
                custom_preface_md=resolved_preface_md,
                org_name=org_name,
                global_score=global_score,
                has_warning=has_warning,
                visible_metadata=visible_metadata,
                layouts=layouts_list,
                cost_estimate=cost,
                total_tokens=t_tokens,
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                reasoning_tokens=r_tokens,
                mcp_tool_audit=mcp_audit_data,
                grouped_extensions=grouped_extensions,
                results=v2_results,
                hydrated_references=v2_hydrated_refs,
                global_synthesis=global_synth,
            )
            return report_dto
        except Exception as e:
            msg = f"Failed to map execution {execution.id} results to ReportDataDTO: {e}"
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e
