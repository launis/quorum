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
        self, execution_id: str, profile_id: str = "default", accept_language: str | None = None
    ) -> ReportDataDTO:
        """Builds the strictly typed report payload by parsing results according to the selected profile."""
        execution = await self.repo.get_execution(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found."
            logger.error(f"[BlueprintTransformer] {ErrorCodes.RESOURCE_NOT_FOUND.name}: {msg}")
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})

        workflow_data = await self.repo.get_workflow_by_id(execution.workflow_id)
        if not workflow_data:
            msg = f"Executing workflow {execution.workflow_id} not found."
            logger.error(f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        from backend_v2.models.state import StateProjector

        projector = StateProjector()
        results = projector.fold_trace(execution.execution_trace)

        locale = accept_language or execution.metadata.get("target_locale", "en")

        import typing

        def _extract_i18n(val: dict[str, typing.Any] | None) -> dict[str, str]:
            """Ensure payload serializes nested I18nText structures into flat dictionaries to pass Pydantic."""
            if val and isinstance(val, dict):
                translations = val.get("translations", val)
                if isinstance(translations, dict):
                    return {str(k): str(v) for k, v in translations.items()}
            return {}

        # Fetch the selected output profile from repository
        default_profile_ref = workflow_data.get("default_profile_id", "default")
        resolved_pid_request = profile_id if profile_id else default_profile_ref

        profile_data = None

        # Pre-fetch all profiles for relation resolution and UI dropdown mapping
        all_profiles_data = await self.repo.get_all_output_profiles()

        # 1. Try to resolve by Exact Opaque ID
        for p_dict in all_profiles_data:
            if p_dict.get("id") == resolved_pid_request:
                profile_data = p_dict
                break

        # 2. Try to resolve by Routing Slug
        if not profile_data:
            for p_dict in all_profiles_data:
                if p_dict.get("slug") == resolved_pid_request:
                    profile_data = p_dict
                    break

        # 3. Fallback to default routing slug if requested was missing completely
        if not profile_data and resolved_pid_request != default_profile_ref:
            logger.warning(f"Profile {resolved_pid_request} not found, falling back to slug '{default_profile_ref}'")
            for p_dict in all_profiles_data:
                if p_dict.get("slug") == default_profile_ref:
                    profile_data = p_dict
                    break

        if not profile_data:
            msg = f"Output profile '{resolved_pid_request}' not found in the database. Failing fast."
            logger.error(f"[BlueprintTransformer] {ErrorCodes.RESOURCE_NOT_FOUND.name}: {msg}")
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})

        resolved_pid = str(profile_data.get("id"))

        from backend_v2.models.domain.output_profile import OutputProfile

        profile = OutputProfile.model_validate(profile_data)

        # Build dropdown options
        available_profiles_map = {}
        for pd in all_profiles_data:
            try:
                op = OutputProfile.model_validate(pd)
                name_dict = _extract_i18n(op.name.model_dump())
                available_profiles_map[op.id] = name_dict.get(locale, name_dict.get("en", op.id))
            except Exception as e:
                logger.warning(
                    f"[BlueprintTransformer] VALIDATION_FAILED: Failed to parse profile for dropdown map: {e}",
                    exc_info=True,
                )

        if resolved_pid not in available_profiles_map:
            name_dict = _extract_i18n(profile.name.model_dump())
            available_profiles_map[resolved_pid] = name_dict.get(locale, name_dict.get("en", resolved_pid))

        profile_name_dict = _extract_i18n(profile.name.model_dump())
        layout_defs = profile.layouts

        layouts_list = []
        # Pre-fetch prompt blocks to enrich axis labels
        all_blocks = await self.repo.get_all_prompt_blocks()
        blocks_by_id = {b["id"]: b for b in all_blocks if "id" in b}

        # Pre-fetch DAG workflow steps for collision avoidance renaming
        workflow_steps = {s["id"]: s for s in workflow_data.get("steps", [])}

        global_score = None

        scoring_out = None
        # Deep search for the unique 'scoring_result' object embedded by the ScoringHook
        # post-hook into ANY dynamical step
        for step_res in results.values():
            if isinstance(step_res, dict) and "scoring_result" in step_res:
                scoring_out = step_res["scoring_result"]
                break

        # Fallback if somehow placed at root
        if not scoring_out and isinstance(results.get("scoring_result"), dict):
            scoring_out = results.get("scoring_result")

        global_score = None
        if isinstance(scoring_out, dict):
            t_score = scoring_out.get("total_score")
            global_score = float(t_score) if t_score is not None else None

        try:
            for layout_def in layout_defs:
                preset_view = layout_def.layout_type.value
                target_blocks = layout_def.components
                # if target_blocks missing, default to empty list. But models say it is guaranteed and non-empty.
                show_text = layout_def.show_text

                layout_title = _extract_i18n(layout_def.title.model_dump())
                layout_desc = _extract_i18n(layout_def.description.model_dump()) if layout_def.description else {}

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

                            is_matrix_category = block and block.get("category_id") == "matrix"
                            is_numeric = (isinstance(v, (int, float)) and not isinstance(v, bool)) or str(v).replace(
                                ".", "", 1
                            ).isdigit()
                            score_float = None

                            # Strict Rendering: Only allow float scores to be parsed for Matrix categories
                            # (or the original global score)
                            if is_numeric and (is_matrix_category or is_legacy_score):
                                try:
                                    score_float = float(v)
                                except (ValueError, TypeError):
                                    score_float = None

                            axis_name = step_id if is_legacy_score else k
                            axis_description = ""
                            scale_min = 0.0
                            scale_max = 0.0  # 0.0 cleanly suppresses UI scaling badges if undefined
                            scale_labels = {}

                            if block:
                                label_obj = block.get("label", {})
                                trans_dict = _extract_i18n(label_obj)
                                axis_name = trans_dict.get(locale, trans_dict.get("en", k)) or k

                                desc_obj = block.get("description", {})
                                trans_dict_desc = _extract_i18n(desc_obj)
                                axis_description = trans_dict_desc.get(locale, trans_dict_desc.get("en", "")) or ""

                                scales_def = block.get("scales", [])
                                if scales_def:
                                    scores = [float(s.get("score", 0)) for s in scales_def if "score" in s]
                                    if scores:
                                        scale_max = max(scores)
                                        scale_min = min(scores)

                                    for s in scales_def:
                                        s_score = float(s.get("score", 0))
                                        s_label_obj = s.get("name", {})
                                        s_trans = _extract_i18n(s_label_obj)
                                        s_label = s_trans.get(locale, s_trans.get("en", ""))
                                        # Only write int cleanly for mapping
                                        cleaned_score = int(s_score) if s_score.is_integer() else s_score
                                        scale_labels[str(cleaned_score)] = s_label

                                # Collision Avoidance
                                original_axis_name = axis_name
                                collision_counter = 1
                                # Check if name is already present in axes from another block
                                while any(ext.name == axis_name for ext in unsorted_axes.values()):
                                    step_node = workflow_steps.get(step_id, {})
                                    step_title_obj = _extract_i18n(step_node.get("name", {})) or _extract_i18n(
                                        step_node.get("title", {})
                                    )
                                    step_title = step_title_obj.get(locale, step_title_obj.get("en", step_id))
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
                if preset_view == "radar_3d" and len(axes) < 3:
                    preset_view = "matrix_2d" if len(axes) == 2 else "box_1d"
                elif preset_view == "matrix_2d" and len(axes) < 2:
                    preset_view = "box_1d"
                elif preset_view == "automatic":
                    # For wildcards or grouped automatic lists, forcing a 3D/2D matrix out of arbitrary
                    # components creates visual garbage. We default to 1D enumerations so they list cleanly.
                    preset_view = "box_1d"

                preset_map = {
                    "box_1d": "1d_metrics",
                    "matrix_2d": "2d_compare",
                    "radar_3d": "3d_complex",
                    "excel_row": "text_only",
                    "automatic": "default",
                }
                mapped_view = preset_map.get(preset_view, "default")
                from typing import Literal, cast

                preset_view_typed = cast(
                    Literal["1d_metrics", "2d_compare", "3d_complex", "default", "text_only"], mapped_view
                )

                if axes or preset_view_typed == "text_only":
                    layouts_list.append(
                        ReportLayoutDTO(
                            preset_view=preset_view_typed,
                            title=layout_title,
                            description=layout_desc,
                            axes=axes,
                            show_text=show_text,
                        )
                    )
        except Exception as e:
            msg = f"Failed to build layout DTO: {e}"
            logger.error(f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
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
                logger.warning(
                    f"[BlueprintTransformer] RESOURCE_NOT_FOUND: Failed to resolve org name "
                    f"for id {execution.organization_id}: {org_err}",
                    exc_info=True,
                )

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
                    f"[BlueprintTransformer] ALARM: Reporting 0 tokens for execution {execution.id}. "
                    "Telemetry or V3 metadata sync might be broken."
                )

            if not layouts_list:
                logger.warning(
                    f"[BlueprintTransformer] ALARM: 0 Layouts generated for execution {execution.id}. "
                    "UI will render empty."
                )

            # Extract MCP Tool Loop audit trail from FrozenContext (XAI Evidence for Frontend)
            mcp_audit_data: list[dict[str, typing.Any]] = []
            if hasattr(execution, "frozen_context") and execution.frozen_context:
                if hasattr(execution.frozen_context, "mcp_tool_audit") and execution.frozen_context.mcp_tool_audit:
                    mcp_audit_data = [t.model_dump(mode="json") for t in execution.frozen_context.mcp_tool_audit]

            dto = ReportDataDTO(
                workflow_id=execution.workflow_id,
                profile_id=resolved_pid,
                profile_name=profile_name_dict,
                available_profiles=available_profiles_map,
                created_at=execution.created_at,
                org_name=org_name,
                global_score=global_score,
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
            logger.error(f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED}
            ) from e
