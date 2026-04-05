"""Blueprint Transformer Service for V3 Extreme MVC."""

import logging

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ReportAxisDTO, ReportDataDTO, ReportLayoutDTO

logger = logging.getLogger(__name__)


class BlueprintTransformer:
    """The Universal Transformer Hub. Parses raw execution results into ReportDataDTO."""

    def __init__(self, repo: AbstractWorkflowRepository):
        self.repo = repo

    async def build_report_dto(
        self, execution_id: str, profile_id: str | None = None, accept_language: str | None = None
    ) -> ReportDataDTO:
        """Builds the strictly typed report payload by parsing results according to the selected profile."""
        execution = await self.repo.get_execution(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})

        workflow_data = await self.repo.get_workflow_by_id(execution.workflow_id)
        if not workflow_data:
            msg = f"Executing workflow {execution.workflow_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        from backend_v2.models.state import StateProjector

        projector = StateProjector()
        results = projector.fold_trace(execution.execution_trace)

        locale = accept_language or execution.metadata.get("target_locale", "en")

        import typing

        def _resolve_i18n_str(val: dict[str, typing.Any] | None, lang: str, fallback: str) -> str:
            """Ensure payload extracts the localized string for axis titles."""
            if val and isinstance(val, dict):
                translations = val.get("translations", val)
                if isinstance(translations, dict):
                    return str(translations.get(lang, translations.get("en", fallback)))
            return fallback

        # Fetch the selected output profile from repository
        default_profile_ref = workflow_data.get("default_profile_id", "default")

        # If API requested "default" explicitly, we should treat it as seeking the workflow's default
        resolved_pid_request = profile_id if profile_id and profile_id != "default" else default_profile_ref

        profile_data = None

        # Pre-fetch all profiles for relation resolution and UI dropdown mapping
        all_profiles_data = await self.repo.get_all_output_profiles()

        # 1. Try to resolve by Exact Opaque ID
        for p_dict in all_profiles_data:
            if p_dict.get("id") == resolved_pid_request:
                profile_data = p_dict
                break

        # 2. Hardcoded fallback for missing 'default' specification in older executions
        if not profile_data and resolved_pid_request == "default":
            logger.warning("Profile ID 'default' requested but not an Opaque ID. Resolving fallback.")
            for p_dict in all_profiles_data:
                # Opaque fallback convention: If 'default' is requested, attempt to resolve the actual ID
                # assigned to the system's "default" named or historically slugged profile.
                if p_dict.get("slug") in ("default", "executive_summary"):
                    profile_data = p_dict
                    break

        if not profile_data:
            msg = f"Output profile '{resolved_pid_request}' not found in the database. Failing fast."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})

        resolved_pid = str(profile_data.get("id"))

        from backend_v2.models.domain.output_profile import OutputProfile

        profile = OutputProfile.model_validate(profile_data)

        # Build dropdown options
        available_profiles_map = {}
        for pd in all_profiles_data:
            try:
                op = OutputProfile.model_validate(pd)
                available_profiles_map[op.id] = op.name
            except Exception as e:
                logger.error(
                    "[BlueprintTransformer] VALIDATION_FAILED: Failed to parse profile for dropdown map: %s",
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message="Failed to parse profile for dropdown map",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                ) from e

        if resolved_pid not in available_profiles_map:
            available_profiles_map[resolved_pid] = profile.name

        profile_name_dict = profile.name
        layout_defs = profile.layouts
        display_scale = getattr(profile, "display_scale", "original")

        layouts_list = []
        # Pre-fetch prompt blocks to enrich axis labels
        all_blocks = await self.repo.get_all_prompt_blocks()
        blocks_by_id = {b["id"]: b for b in all_blocks if "id" in b}

        # Pre-fetch DAG workflow steps for collision avoidance renaming
        workflow_steps = {s["id"]: s for s in workflow_data.get("steps", [])}

        global_score = None

        has_warning = False
        synthesis_md = None
        scoring_out = None
        for step_res in results.values():
            if isinstance(step_res, dict):
                if "scoring_result" in step_res:
                    scoring_out = step_res["scoring_result"]
                if step_res.get("has_warning"):
                    has_warning = True
                if step_res.get("synthesized_markdown"):
                    synthesis_md = step_res.get("synthesized_markdown")

        # Load section_syntheses if available from SSOT
        profile_cache = execution.profile_syntheses.get(resolved_pid)
        section_syntheses = {}
        synthesis_md = None
        if profile_cache:
            section_syntheses = profile_cache.section_syntheses
            synthesis_md = profile_cache.synthesized_markdown

        if results.get("has_warning"):
            has_warning = True

        global_score = None
        if isinstance(scoring_out, dict):
            t_score = scoring_out.get("total_score")
            global_score = float(round(float(t_score), 1)) if t_score is not None else None

        try:
            for layout_def in layout_defs:
                preset_view = layout_def.preset_view
                target_blocks = layout_def.target_blocks
                # if target_blocks missing, default to empty list. But models say it is guaranteed and non-empty.
                show_text = layout_def.show_text

                layout_title = layout_def.title
                layout_desc = layout_def.description

                axes: list[ReportAxisDTO] = []
                unsorted_axes: dict[str, ReportAxisDTO] = {}
                # Ensure unique key generation for collisions across steps
                for step_id, step_data in results.items():
                    if isinstance(step_data, dict):
                        for k, v in step_data.items():
                            # Determine if this key should be included in this layout
                            if target_blocks and "*" not in target_blocks and k not in target_blocks:
                                continue

                            is_legacy_score = k == "score"
                            suffix_list = [
                                "_justification",
                                "_scaled",
                                "_normalized",
                                "_raw",
                                "_cited_source_id",
                                "_cited_text_quote",
                                "_google_citation",
                                "_coaching",
                                "_confidence",
                                "_falsification",
                                "_missing_context",
                                "_risk_flag",
                                "_remediation_steps",
                                "_emotional_sentiment",
                                "_theory_link",
                            ]
                            is_suffix_key = any(k.endswith(sfx) for sfx in suffix_list)
                            if is_suffix_key:
                                continue

                            block = blocks_by_id.get(k)

                            # Adhere to Fail-Fast / Strict Domain Logic: Only print if key is a known Model
                            # Block (or legacy score)
                            if not block and not is_legacy_score:
                                continue

                            # --- Epic 12: View Scale Selection ---
                            active_score_key = k
                            if not is_legacy_score:
                                if display_scale == "custom":
                                    active_score_key = f"{k}_scaled"
                                elif display_scale == "normalized_100":
                                    active_score_key = f"{k}_normalized"

                            target_val = step_data.get(active_score_key, v)

                            is_matrix_category = block and block.get("category_id") == "matrix"
                            is_num_type = isinstance(target_val, (int, float)) and not isinstance(target_val, bool)
                            is_numeric = is_num_type or str(target_val).replace(".", "", 1).isdigit()
                            score_float = None

                            # Strict Rendering: Only allow float scores to be parsed for Matrix categories
                            # (or the original global score)
                            if is_numeric and (is_matrix_category or is_legacy_score):
                                try:
                                    if target_val is not None:
                                        raw_f = float(target_val)
                                        if display_scale == "normalized_100":
                                            score_float = float(round(raw_f))
                                        else:
                                            # Epic 13: Preserve variations (1 decimal) for custom/original views.
                                            score_float = float(round(raw_f, 1))
                                except (ValueError, TypeError) as e:
                                    logger.error("Failed to parse score to float", exc_info=True)
                                    raise AppException(
                                        message=f"Invalid numeric score: {target_val}",
                                        details={"error_code": ErrorCodes.VALIDATION_FAILED},
                                        status_code=400,
                                    ) from e

                            axis_name = step_id if is_legacy_score else k
                            axis_description = ""
                            scale_min = 0.0
                            scale_max = 0.0  # 0.0 cleanly suppresses UI scaling badges if undefined
                            scale_labels: dict[str, str] = {}

                            if block:
                                label_obj = block.get("label", {})
                                axis_name = _resolve_i18n_str(label_obj, locale, k) or k

                                desc_obj = block.get("description", {})
                                axis_description = _resolve_i18n_str(desc_obj, locale, "")

                                scales_def = block.get("scales", [])

                                # Epic 12: Handle UI Visual Scale Boundaries
                                if display_scale == "normalized_100" and is_matrix_category:
                                    scale_min = 0.0
                                    scale_max = 100.0
                                    scale_labels = {}  # Purge mapping to prevent disproportionate labeling
                                elif scales_def:
                                    scores = [float(s.get("score", 0)) for s in scales_def if "score" in s]
                                    if scores:
                                        scale_max = max(scores)
                                        scale_min = min(scores)

                                    for s in scales_def:
                                        s_score = float(s.get("score", 0))
                                        s_label_obj = s.get("name", {})
                                        s_label = _resolve_i18n_str(s_label_obj, locale, "")
                                        # Only write int cleanly for mapping
                                        cleaned_score = int(s_score) if s_score.is_integer() else s_score
                                        scale_labels[str(cleaned_score)] = s_label

                                # Collision Avoidance
                                original_axis_name = axis_name
                                collision_counter = 1
                                # Check if name is already present in axes from another block
                                while any(ext.name == axis_name for ext in unsorted_axes.values()):
                                    step_node = workflow_steps.get(step_id, {})
                                    step_title_obj = step_node.get("name", {}) or step_node.get("title", {})
                                    step_title = _resolve_i18n_str(step_title_obj, locale, step_id)
                                    axis_name = f"{original_axis_name} ({step_title})"
                                    if any(ext.name == axis_name for ext in unsorted_axes.values()):
                                        axis_name = f"{original_axis_name} ({step_title} {collision_counter})"
                                        collision_counter += 1

                                justification = ""
                                cited_source_id = ""
                                cited_text_quote = ""
                                cited_web_citation = ""
                                coaching = None
                                confidence = None
                                falsification = None
                                missing_context = None
                                risk_flag = None
                                remediation_steps = None
                                emotional_sentiment = None
                                theory_link = None

                                if show_text:
                                    if is_legacy_score:
                                        justification = str(step_data.get("justification", ""))
                                    else:
                                        eval_notes = step_data.get("evaluation_notes", "")
                                        justification = str(step_data.get(f"{k}_justification", eval_notes) or "")
                                    cited_source_id = str(step_data.get(f"{k}_cited_source_id", ""))
                                    cited_text_quote = str(step_data.get(f"{k}_cited_text_quote", ""))
                                    cited_web_citation = str(step_data.get(f"{k}_google_citation", ""))

                                    coaching = step_data.get(f"{k}_coaching")
                                    confidence = step_data.get(f"{k}_confidence")
                                    falsification = step_data.get(f"{k}_falsification")
                                    missing_context = step_data.get(f"{k}_missing_context")
                                    risk_flag = step_data.get(f"{k}_risk_flag")
                                    remediation_steps = step_data.get(f"{k}_remediation_steps")
                                    emotional_sentiment = step_data.get(f"{k}_emotional_sentiment")
                                    theory_link = step_data.get(f"{k}_theory_link")

                                # Use a combined key for uniqueness
                                unique_k = f"{step_id}_{k}"
                                unsorted_axes[unique_k] = ReportAxisDTO(
                                    name=axis_name,
                                    description=axis_description,
                                    score=score_float,
                                    justification=justification,
                                    cited_source_id=cited_source_id,
                                    cited_text_quote=cited_text_quote,
                                    cited_web_citation=cited_web_citation,
                                    coaching=coaching,
                                    confidence=confidence,
                                    falsification=falsification,
                                    missing_context=missing_context,
                                    risk_flag=risk_flag,
                                    remediation_steps=remediation_steps,
                                    emotional_sentiment=emotional_sentiment,
                                    theory_link=theory_link,
                                    scale_min=scale_min,
                                    scale_max=scale_max,
                                    scale_labels=scale_labels,
                                )

                axes = list(unsorted_axes.values())

                # Graceful Degradation (BFF Capability - Zero Math Frontend)
                if preset_view == "3d_complex" and len(axes) < 3:
                    preset_view = "2d_compare" if len(axes) == 2 else "1d_metrics"
                elif preset_view == "2d_compare" and len(axes) < 2:
                    preset_view = "1d_metrics"

                if axes or preset_view == "text_only":
                    synthesis_config = getattr(layout_def, "synthesis", None)
                    if layout_title:
                        title_str = (
                            str(layout_title.model_dump()) if hasattr(layout_title, "model_dump") else str(layout_title)
                        )
                    else:
                        title_str = ""
                    layout_id = f"layout_{preset_view}_{str(hash(title_str))}"

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
                            show_text=show_text,
                            synthesis=synthesis_config,
                            synthesis_md=section_md,
                        )
                    )

            final_synthesis = None
            if synthesis_md:
                # M3 Output Management Hardening: Bleach HTML XSS Sanitization
                import bleach  # type: ignore[import-untyped]

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
                org = await self.repo.get_organization(execution.organization_id)
                if org and "name" in org:
                    org_name = str(org["name"])
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
                for _step_key, step_data in results.items():
                    if isinstance(step_data, dict) and "_step_metadata" in step_data:
                        usage = step_data["_step_metadata"].get("token_usage", {})
                        if isinstance(usage, dict):
                            p_tokens += usage.get("prompt_tokens", 0)
                            c_tokens += usage.get("completion_tokens", 0)
                            r_tokens += usage.get("reasoning_tokens", 0)
                            t_tokens += usage.get("total_tokens", 0)
                            cost += float(usage.get("cost_usd", 0.0))

            # Backward compatibility / fallback for tests
            if t_tokens == 0:
                cost = getattr(execution, "cost_estimate", 0.0)
                p_tokens = getattr(execution, "prompt_tokens", 0)
                c_tokens = getattr(execution, "completion_tokens", 0)
                r_tokens = getattr(execution, "reasoning_tokens", 0)
                t_tokens = getattr(execution, "total_tokens", 0)

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
            from backend_v2.models.v2_core import MCPAuditTrace

            mcp_audit_data: list[MCPAuditTrace] = []
            if hasattr(execution, "frozen_context") and execution.frozen_context:
                if hasattr(execution.frozen_context, "mcp_tool_audit") and execution.frozen_context.mcp_tool_audit:
                    mcp_audit_data = execution.frozen_context.mcp_tool_audit

            visible_metadata = getattr(profile, "visible_metadata", [])

            dto = ReportDataDTO(
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
            )
            return dto
        except Exception as e:
            msg = f"Failed to map execution {execution.id} results to ReportDataDTO: {e}"
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED}
            ) from e
