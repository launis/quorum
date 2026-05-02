"""Blueprint Transformer Service for V3 Extreme MVC."""

import logging
import re
from typing import Any

import bleach

from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.report import TraceMatrixPayloadDTO, TraceScoringPayloadDTO
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import (
    MatrixScorecardRowDTO,
    MCPAuditTrace,
    PromptBlock,
    ReportDataDTO,
    ReportLayoutDTO,
    Workflow,
)

logger = logging.getLogger(__name__)


class BlueprintTransformer:
    """The Universal Transformer Hub. Parses raw execution results into ReportDataDTO."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        identity_repo: IIdentityRepository,
    ):
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.identity_repo = identity_repo

    async def build_report_dto(
        self, execution_id: str, profile_id: str | None = None, accept_language: str | None = None
    ) -> ReportDataDTO:
        """Builds the strictly typed report payload by parsing results according to the selected profile."""
        execution = await self.exec_repo.get_execution(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})

        workflow_data = await self.workflow_repo.get_workflow_by_id(execution.workflow_id)
        if not workflow_data:
            msg = f"Executing workflow {execution.workflow_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        projector = StateProjector()
        results = projector.fold_trace(execution.execution_trace)

        locale = accept_language or execution.metadata.get("target_locale") or "en"

        def _resolve_i18n_str(val: dict[str, Any] | None, lang: str, fallback: str) -> str:
            """Ensure payload extracts the localized string for axis titles."""
            if val and isinstance(val, dict):
                translations = val.get("translations") or val
                if isinstance(translations, dict):
                    return str(translations.get(lang) or translations.get("en") or fallback)
            return fallback

        def _clean_hallucinated_numbers(text: str) -> str:
            """Removes sentences that contain numeric evaluations (e.g. 'Taso 3') to prevent hallucinations."""
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

        workflow_obj = Workflow.model_validate(workflow_data)

        # Fetch the selected output profile from repository
        default_profile_ref = workflow_obj.default_profile_id

        # If API requested "default" explicitly, we should treat it as seeking the workflow's default
        resolved_pid_request = profile_id if profile_id and profile_id != "default" else default_profile_ref

        # Pre-fetch all profiles for relation resolution and UI dropdown mapping
        all_profiles_data = await self.comp_repo.get_all_output_profiles()
        all_profiles = []
        for pd in all_profiles_data:
            try:
                all_profiles.append(OutputProfile.model_validate(pd))
            except Exception as e:
                logger.error(
                    "[BlueprintTransformer] VALIDATION_FAILED: Failed to parse profile: %s",
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message="Failed to parse profile from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                ) from e

        # 1. Try to resolve by Exact Opaque ID
        profile = next((p for p in all_profiles if p.id == resolved_pid_request), None)

        if not profile:
            msg = f"Output profile '{resolved_pid_request}' not found in the database. Failing fast."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})

        resolved_pid = str(profile.id)

        # Build dropdown options
        available_profiles_map = {p.id: p.name for p in all_profiles}

        if resolved_pid not in available_profiles_map:
            available_profiles_map[resolved_pid] = profile.name

        profile_name_dict = profile.name
        layout_defs = profile.layouts
        display_scale = getattr(profile, "display_scale", "original")

        # Epic: XAI Output Extensions
        visible_extensions = [v.value for v in getattr(profile, "visible_extensions", [])]
        grouped_extensions: dict[str, list[Any]] = {ext: [] for ext in visible_extensions}

        # We must pre-fetch blocks early for resolving axis_label
        all_blocks = await self.comp_repo.get_all_prompt_blocks()
        blocks_by_id: dict[str, PromptBlock] = {}
        for b in all_blocks:
            if "id" in b:
                try:
                    blocks_by_id[b["id"]] = PromptBlock.model_validate(b)
                except Exception as e:
                    logger.error(
                        "[BlueprintTransformer] %s: Failed to parse PromptBlock %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        b.get("id"),
                        exc_info=True,
                    )
                    raise AppException(
                        message=f"Failed to parse PromptBlock {b.get('id')} from database",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e
        layouts_list = []
        # Pre-fetch prompt blocks to enrich axis labels
        # (Blocks already fetched above for global aggregation)

        # Pre-fetch DAG workflow steps for collision avoidance renaming
        workflow_steps = {s.id: s for s in workflow_obj.steps} if workflow_obj.steps else {}

        global_score = None

        has_warning = False
        synthesis_md = None
        scoring_out = None

        for dto in results:
            if dto.block_id == "scoring_result" and isinstance(dto.payload, dict):
                scoring_out = dto.payload
            if dto.block_id == "has_warning" and dto.payload:
                has_warning = True
            if dto.block_id == "synthesized_markdown" and dto.payload:
                synthesis_md = dto.payload

        profile_cache = execution.profile_syntheses.get(resolved_pid)
        original_synthesis_md = synthesis_md
        section_syntheses: dict[str, str] = {}
        xai_highlights_cache: list[Any] = []
        if profile_cache:
            section_syntheses = getattr(profile_cache, "section_syntheses", {})
            val = getattr(profile_cache, "synthesized_markdown", original_synthesis_md)
            synthesis_md = val or original_synthesis_md
            xai_highlights_cache = getattr(profile_cache, "xai_highlights", [])
        else:
            synthesis_md = original_synthesis_md

        # Merge XAI Highlights from cache into grouped_extensions
        for highlight in xai_highlights_cache:
            # Pydantic Mandate: Kaikki tulee tietokannasta validaation läpi luokkana
            t_name = highlight.extension_type

            if not t_name:
                raise AppException(
                    message="Fail-Fast: Cached XaiHighlightItem missing 'extension_type'.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            group_key = t_name.lower().replace(" ", "_")
            if group_key not in grouped_extensions:
                grouped_extensions[group_key] = []

            # Epic 10: Map the synthesized global highlight so it outranks fragmented matrix extensions.
            # We omit 'axis_name' so it doesn't render a 'teoriaotsikko' in the UI.
            grouped_extensions[group_key].append(
                {group_key: highlight.content, "content": highlight.content, "_score": -999.0, "_is_synthesized": True}
            )

        if any(dto.block_id == "has_warning" and dto.payload for dto in results):
            has_warning = True

        global_score = None
        penalties_applied: list[str] = []
        if isinstance(scoring_out, dict):
            # Enforce Fail-Fast Hydration Mandate
            try:
                score_dto = TraceScoringPayloadDTO.model_validate(scoring_out)
                t_score = score_dto.total_score
                global_score = float(round(float(t_score), 1)) if t_score is not None else None
                raw_penalties = score_dto.penalties_applied
                if isinstance(raw_penalties, list):
                    penalties_applied = [str(p) for p in raw_penalties]
            except Exception as e:
                logger.debug("Scoring payload extraction failed: %s", e)

        evaluative_matrices: list[MatrixScorecardRowDTO] = []
        informational_matrices: list[MatrixScorecardRowDTO] = []
        all_parsed_matrices: dict[str, MatrixScorecardRowDTO] = {}

        # Grand Unification: Single extraction loop for all Matrix blocks
        for dto in results:
            step_id = dto.step_id
            b_id = dto.block_id
            block_data = dto.payload

            if not isinstance(block_data, dict):
                continue

            pb_meta = blocks_by_id.get(b_id)
            # Fail-Fast: Only parse actual matrix blocks defined in the database
            if not pb_meta or pb_meta.category_id != "matrix":
                continue

            # Epic 39 / Phase 9 Extraction (Fail-Fast Hydration Mandate)
            try:
                matrix_payload = TraceMatrixPayloadDTO.model_validate(block_data)
            except Exception as e:
                logger.debug("Skipping block %s due to invalid matrix payload format: %s", b_id, e)
                continue

            raw_score = matrix_payload.raw_score

            if raw_score is None:
                continue  # Valid Fail-Fast: Only include matrices that were actually scored

            norm_score = matrix_payload.normalized_score

            # Extrema & Localization
            axis_name = pb_meta.label.resolve(locale) if pb_meta.label else b_id
            if not axis_name:
                axis_name = b_id
            if pb_meta.is_evaluative:
                axis_name += " *"

            label_fi = pb_meta.label.resolve("fi") if pb_meta.label else b_id
            label_en = pb_meta.label.resolve("en") if pb_meta.label else b_id
            axis_description = pb_meta.description.resolve(locale) if pb_meta.description else ""

            if pb_meta.computed_min is None or pb_meta.computed_max is None:
                raise AppException(
                    message=f"PromptBlock '{b_id}' missing Pydantic computed_min/max.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            scale_min = float(pb_meta.computed_min)
            scale_max = float(pb_meta.computed_max)

            scales_def = pb_meta.scales
            if not scales_def:
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

                if s_score == scale_min:
                    ui_boundary_labels["0.0"] = s_label
                if s_score == scale_max:
                    ui_boundary_labels["1.0"] = s_label

            # Output override logic
            display_scale_min = scale_min
            display_scale_max = scale_max

            active_score_key = "raw_score"
            if display_scale == "normalized_100":
                active_score_key = "normalized_score"
                display_scale_min = 0.0
                display_scale_max = 100.0
                level_names = {}  # Purge mapping to prevent disproportionate labeling
            elif display_scale == "custom":
                # Custom bounds are from pb_meta scale_min/scale_max
                scale_min_val = pb_meta.scale_min
                scale_max_val = pb_meta.scale_max
                if scale_min_val is None or scale_max_val is None:
                    raise AppException(
                        message=f"UI bounds missing for PromptBlock '{b_id}' under custom scale.",
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
                display_scale_min = float(scale_min_val)
                display_scale_max = float(scale_max_val)

            target_val = getattr(matrix_payload, active_score_key, None)
            if target_val is None:
                target_val = raw_score

            score_float = float(round(float(target_val), 1)) if target_val is not None else 0.0
            if display_scale == "normalized_100":
                score_float = float(round(score_float))

            # Plot ratio ALWAYS uses raw mathematical extrema, not display scale
            # Fail-Fast logic guarantees scale_max > scale_min and raw_score is present
            ratio = (float(raw_score) - scale_min) / (scale_max - scale_min)
            ui_plot_ratio = float(max(0.0, min(1.0, ratio)))

            # Collision Avoidance
            original_axis_name = axis_name
            collision_counter = 1
            while any(ext.name == axis_name for ext in all_parsed_matrices.values()):
                step_node = workflow_steps.get(step_id)
                step_title = step_id
                if step_node:
                    name_obj = getattr(step_node, "name", None) or getattr(step_node, "title", None)
                    if name_obj and hasattr(name_obj, "resolve"):
                        step_title = name_obj.resolve(locale)
                    elif isinstance(name_obj, str):
                        step_title = name_obj
                    elif isinstance(name_obj, dict):
                        step_title = _resolve_i18n_str(name_obj, locale, step_id)
                axis_name = f"{original_axis_name} ({step_title})"
                if any(ext.name == axis_name for ext in all_parsed_matrices.values()):
                    axis_name = f"{original_axis_name} ({step_title} {collision_counter})"
                    collision_counter += 1

            # Legacy justifications and extensions
            justification = matrix_payload.justification
            if not justification:
                raise AppException(
                    message=f"Fail-Fast: Missing justification for matrix block '{b_id}'",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            # Breakdowns
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
                            raise AppException(
                                message=(f"Fail-Fast: Invalid level key '{lvl_key}' in matrix breakdown for '{b_id}'."),
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            ) from v_err
                axis_level_breakdown = clean_level_dict

            ext_dict = matrix_payload.extensions or {}

            true_atoms = None
            total_atoms = None
            if matrix_payload.evaluated_atoms:
                true_atoms = sum(1 for v in matrix_payload.evaluated_atoms.values() if v)
                total_atoms = len(matrix_payload.evaluated_atoms)

            row_dto = MatrixScorecardRowDTO(
                block_id=b_id,
                name=axis_name,
                label_fi=label_fi,
                label_en=label_en,
                description=axis_description,
                score=score_float,
                scale_min=display_scale_min,
                scale_max=display_scale_max,
                normalized_score=float(norm_score) if norm_score is not None else None,
                true_atoms=true_atoms,
                total_atoms=total_atoms,
                justification=_clean_hallucinated_numbers(justification),
                evidence_type=ext_dict.get("evidence_type"),
                missing_context=ext_dict.get("missing_context") or "",
                cited_source_id=ext_dict.get("source_id"),
                cited_text_quote=ext_dict.get("citation"),
                cited_web_citation=ext_dict.get("google_citation"),
                coaching=ext_dict.get("coaching"),
                confidence=ext_dict.get("confidence"),
                falsification=ext_dict.get("falsification"),
                risk_flag=ext_dict.get("risk_flag"),
                remediation_steps=ext_dict.get("remediation_steps"),
                emotional_sentiment=ext_dict.get("emotional_sentiment"),
                theory_link=ext_dict.get("theory_link"),
                level_breakdown=axis_level_breakdown,
                level_names=level_names,
                ui_boundary_labels=ui_boundary_labels,
                ui_plot_ratio=ui_plot_ratio,
                is_evaluative=pb_meta.is_evaluative,
            )

            unique_k = f"{step_id}_{b_id}"
            all_parsed_matrices[unique_k] = row_dto

            # Epic 10/12: Aggregate Matrix-Level XAI Extensions into grouped_extensions for the UI
            for ext_key, ext_val in ext_dict.items():
                # Only map extensions that are requested in the OutputProfile's visible_extensions
                if ext_val and ext_key in grouped_extensions:
                    grouped_extensions[ext_key].append(
                        {
                            "axis_name": axis_name,
                            ext_key: ext_val,
                            "_score": score_float,
                        }
                    )

        # Epic 10: Sort and limit the XAI extensions based on max_extension_items from OutputProfile
        max_items = getattr(profile, "max_extension_items", 2)
        if max_items is not None and max_items > 0:
            for ext_key in grouped_extensions:
                # If a synthesized global highlight exists, it EXCLUSIVELY takes over the category
                # suppressing all raw fragmented matrix extensions (no theory titles).
                synthesized = [x for x in grouped_extensions[ext_key] if x.get("_is_synthesized")]
                if synthesized:
                    grouped_extensions[ext_key] = synthesized[:max_items]
                else:
                    # ZERO-COMPROMISE / FAIL-FAST: No Graceful Degradation.
                    # If global synthesis failed to produce an insight, we do not fallback
                    # to showing fragmented matrix outputs.
                    grouped_extensions[ext_key] = []

        try:
            for idx, layout_def in enumerate(layout_defs):
                preset_view = layout_def.preset_view
                target_blocks = layout_def.target_blocks
                # if target_blocks missing, default to empty list. But models say it is guaranteed and non-empty.
                text_delivery_mode = layout_def.text_delivery_mode

                layout_title = layout_def.title
                layout_desc = layout_def.description

                unsorted_axes = all_parsed_matrices

                # Epic 13: Enforce strict 3D Tuple Ordinality (X, Y, Z)
                # Dictionary iteration is non-deterministic. We MUST sort the extracted axes
                # according to the explicitly provided `target_blocks` array order.
                axes = []
                if target_blocks and "*" not in target_blocks:
                    for target_k in target_blocks:
                        # Phase 3: Exact Opaque ID match, no .endswith()
                        matched = next((axis for axis in unsorted_axes.values() if axis.block_id == target_k), None)
                        if matched:
                            axes.append(matched)
                else:
                    axes = list(unsorted_axes.values())

                # Strict Fail-Fast Constraint: Do not degrade missing UI inputs silently
                if preset_view == "3d_complex" and len(axes) < 3:
                    msg = (
                        f"Layout '{layout_title}' requires at least 3 axes for "
                        f"3d_complex view, but only found {len(axes)}."
                    )
                    logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    )
                elif preset_view == "2d_compare" and len(axes) < 2:
                    msg = (
                        f"Layout '{layout_title}' requires at least 2 axes for "
                        f"2d_compare view, but only found {len(axes)}."
                    )
                    logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    )

                if axes or preset_view == "text_only":
                    synthesis_config = getattr(layout_def, "synthesis", None)
                    layout_id = f"layout_{idx}_{preset_view}"

                    section_md = None
                    if synthesis_config:
                        # Extract exact Section-Level synthesis generated by text_consolidation_hook
                        if layout_id in section_syntheses:
                            section_md = section_syntheses[layout_id]

                    layouts_list.append(
                        ReportLayoutDTO(
                            preset_view=preset_view,
                            title=layout_title,
                            description=layout_desc,
                            axes=axes,
                            text_delivery_mode=text_delivery_mode,
                            synthesis=synthesis_config,
                            synthesis_md=section_md,
                        )
                    )

            final_synthesis = None
            if synthesis_md:
                # M3 Output Management Hardening: Bleach HTML XSS Sanitization

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
                allowed_attributes = {
                    "*": ["class", "id"],
                    "a": ["href", "title", "target"],
                }

                safe_md = bleach.clean(str(synthesis_md), tags=allowed_tags, attributes=allowed_attributes, strip=True)
                final_synthesis = safe_md
        except AppException:
            # Propagate expected fail-fast domain exceptions without wrapping
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
                # Need to lookup organisation if possible
                org_data = await self.identity_repo.get_organization(execution.organization_id)
                if org_data:
                    org = Organization.model_validate(org_data)
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
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND},
                ) from org_err

        try:
            # Event Sensed V3 Token Aggregation
            p_tokens = 0
            c_tokens = 0
            r_tokens = 0
            t_tokens = 0
            cost = 0.0

            if execution.execution_trace:
                for dto in results:
                    if dto.block_id == "_step_metadata" and isinstance(dto.payload, dict):
                        usage = dto.payload.get("token_usage")
                        if isinstance(usage, dict):
                            p_tokens += int(usage["prompt_tokens"]) if "prompt_tokens" in usage else 0
                            c_tokens += int(usage["completion_tokens"]) if "completion_tokens" in usage else 0
                            r_tokens += int(usage["reasoning_tokens"]) if "reasoning_tokens" in usage else 0
                            t_tokens += int(usage["total_tokens"]) if "total_tokens" in usage else 0
                            cost += float(usage["cost_usd"]) if "cost_usd" in usage else 0.0

            # --- V3 SANITY CHECK / HEALTH ALERTS ---
            if t_tokens == 0 and execution.execution_trace:
                logger.warning(
                    "[BlueprintTransformer] ALARM: 0 tokens for %s. Telemetry missing.",
                    execution.id,
                )

            if not layouts_list:
                logger.warning(
                    "[BlueprintTransformer] ALARM: 0 Layouts generated for execution %s. UI will render empty.",
                    execution.id,
                )

            # Extract MCP Tool Loop audit trail from FrozenContext (XAI Evidence for Frontend)
            # FrozenContext is always a Pydantic model; access mcp_tool_audit via strict dot notation.
            mcp_audit_data: list[MCPAuditTrace] = []
            raw_audits: list[MCPAuditTrace] = execution.frozen_context.mcp_tool_audit
            if raw_audits:
                seen_audits: set[str] = set()
                for audit in raw_audits:
                    audit_hash = f"{audit.tool_id}::{audit.query}"
                    if audit_hash not in seen_audits:
                        seen_audits.add(audit_hash)
                        mcp_audit_data.append(audit)

            visible_metadata = getattr(profile, "visible_metadata", [])

            # Deterministic Population of global scorecard arrays
            seen_matrix_ids = set()
            for axis in all_parsed_matrices.values():
                if axis.block_id not in seen_matrix_ids:
                    seen_matrix_ids.add(axis.block_id)
                    if axis.is_evaluative:
                        evaluative_matrices.append(axis)
                    else:
                        informational_matrices.append(axis)

            report_dto = ReportDataDTO(
                strictness_level=execution.strictness_level,
                workflow_id=execution.workflow_id,
                profile_id=resolved_pid,
                profile_name=profile_name_dict,
                available_profiles=available_profiles_map,
                created_at=execution.created_at,
                org_name=org_name,
                global_score=global_score,
                has_warning=has_warning,
                synthesized_markdown=final_synthesis,
                visible_metadata=visible_metadata,
                layouts=layouts_list,
                cost_estimate=cost,
                total_tokens=t_tokens,
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                reasoning_tokens=r_tokens,
                mcp_tool_audit=mcp_audit_data,
                grouped_extensions=grouped_extensions,
                penalties_applied=penalties_applied,
                evaluative_matrices=evaluative_matrices,
                informational_matrices=informational_matrices,
            )
            return report_dto
        except Exception as e:
            msg = f"Failed to map execution {execution.id} results to ReportDataDTO: {e}"
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED}
            ) from e
