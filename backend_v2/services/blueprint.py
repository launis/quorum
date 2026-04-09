"""Blueprint Transformer Service for V3 Extreme MVC."""

import logging

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import XaiExtensionType
from backend_v2.models.v2_core import ReportAxisDTO, ReportDataDTO, ReportLayoutDTO
from backend_v2.models.view.sdui import HighlightBoxDisplay

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

        # Epic: XAI Output Extensions
        visible_extensions = [v.value for v in getattr(profile, "visible_extensions", [])]
        grouped_extensions: dict[str, list[typing.Any]] = {ext: [] for ext in visible_extensions}
        max_extension_items = getattr(profile, "max_extension_items", None)

        # -- GLOBAL XAI EXTENSION AGGREGATION --
        # Aggregate XAI extensions globally across all execution steps before processing layout constraints.
        # This ensures extensions are collected even if a block is excluded from visual charts or show_text is false.
        def _add_ext(group: str, val_key: str, content: typing.Any, axis: str, score: float | int | None = None) -> None:
            camel_group = "".join(word.capitalize() if i > 0 else word for i, word in enumerate(group.split("_")))
            if (group not in visible_extensions and camel_group not in visible_extensions) or content is None or content == "":
                return
            if group not in grouped_extensions:
                grouped_extensions[group] = []
            
            # Deduplicate by exact content match
            for existing in grouped_extensions[group]:
                exist_content = existing.content if isinstance(existing, HighlightBoxDisplay) else existing.get("content")
                if exist_content == content or (isinstance(existing, dict) and existing.get(val_key) == content):
                    # We skip axis merging for HighlightBoxDisplay objects right now for simplicity 
                    # since they are structurally complete, but we could extend it if necessary.
                    if isinstance(existing, dict):
                        if axis not in existing.get("axis_name", ""):
                            existing["axis_name"] = existing.get("axis_name", "") + f" & {axis}"
                        if score is not None and score < existing.get("_score", 999):
                            existing["_score"] = score
                    # For HighlightBoxDisplay, deduplication drops the duplicate completely.
                    return
            
            color_theme: typing.Literal["danger", "info", "warning", "success", "primary"] = "info"
            icon_name = "info"
            
            if group in [XaiExtensionType.FALSIFICATION.value, XaiExtensionType.RISK_FLAG.value]:
                color_theme = "danger"
                icon_name = "warning"
            elif group in [XaiExtensionType.COACHING.value, XaiExtensionType.REMEDIATION_STEPS.value, XaiExtensionType.MISSING_CONTEXT.value]:
                color_theme = "warning"
                icon_name = "lightbulb"
            elif group in [XaiExtensionType.THEORY_LINK.value]:
                color_theme = "info"
                icon_name = "psychology"
            elif group in [XaiExtensionType.EMOTIONAL_SENTIMENT.value, XaiExtensionType.CONFIDENCE.value]:
                color_theme = "success"
                icon_name = "check"

            # Render as strictly typed UI Box instead of Naked Dict
            box = HighlightBoxDisplay(
                content=str(content),
                color_theme=color_theme,
                icon_name=icon_name,
            )
            # Monkey-patch internal fields needed for algorithmic processing before final serialization
            box._score = score if score is not None else 999
            
            grouped_extensions[group].append(box)

        # We must pre-fetch blocks early for resolving axis_label
        all_blocks = await self.repo.get_all_prompt_blocks()
        blocks_by_id = {b["id"]: b for b in all_blocks if "id" in b}

        for step_id, step_data_res in results.items():
            if isinstance(step_data_res, dict):
                for k, v in step_data_res.items():
                    is_legacy_score = k == "score"
                    
                    suffix_list = [
                        "_justification", "_scaled", "_normalized", "_raw",
                        "_cited_source_id", "_cited_text_quote", "_google_citation",
                        "_coaching", "_confidence", "_falsification", "_missing_context",
                        "_risk_flag", "_remediation_steps", "_emotional_sentiment", "_theory_link",
                    ]
                    if any(k.endswith(sfx) for sfx in suffix_list):
                        continue
                        
                    block = blocks_by_id.get(k)
                    if not block and not is_legacy_score:
                        continue
                        
                    axis_name = step_id if is_legacy_score else k
                    if block:
                        label_obj = block.get("label", {})
                        axis_name = _resolve_i18n_str(label_obj, locale, k) or k
                        
                    # Build Ext Vars
                    if is_legacy_score:
                        raw_justification = str(step_data_res.get("justification", ""))
                        raw_cited_source_id = ""
                        raw_cited_text_quote = ""
                        raw_cited_web_citation = ""
                        raw_falsification = None
                        raw_theory_link = None
                        raw_risk_flag = None
                        coaching = None
                        confidence = None
                        missing_context = None
                        remediation_steps = None
                        emotional_sentiment = None
                    else:
                        if isinstance(v, dict):
                            eval_notes = v.get("evaluation_notes", "")
                            raw_justification = str(v.get("step_3_logical_friction", eval_notes) or "")
                            raw_cited_source_id = str(v.get("step_1b_cited_source_id", ""))
                            raw_cited_text_quote = str(v.get("step_1_evidence_quote", ""))
                            raw_cited_web_citation = str(v.get("step_1c_google_citation", ""))
                            raw_falsification = v.get("extension_falsification", v.get("step_2_falsification"))
                            raw_theory_link = v.get("extension_theory_link")
                            raw_risk_flag = v.get("extension_risk_flag")
                            coaching = v.get("extension_coaching")
                            confidence = v.get("extension_confidence")
                            missing_context = v.get("extension_missing_context")
                            remediation_steps = v.get("extension_remediation_steps")
                            emotional_sentiment = v.get("extension_emotional_sentiment")
                        else:
                            eval_notes = step_data_res.get("evaluation_notes", "")
                            raw_justification = str(step_data_res.get("step_3_logical_friction", eval_notes) or "")
                            raw_cited_source_id = str(step_data_res.get("step_1b_cited_source_id", ""))
                            raw_cited_text_quote = str(step_data_res.get("step_1_evidence_quote", ""))
                            raw_cited_web_citation = str(step_data_res.get("step_1c_google_citation", ""))
                            raw_falsification = step_data_res.get("step_2_falsification")
                            raw_theory_link = step_data_res.get("extension_theory_link")
                            raw_risk_flag = step_data_res.get("extension_risk_flag")
                            coaching = step_data_res.get("extension_coaching")
                            confidence = step_data_res.get("extension_confidence")
                            missing_context = step_data_res.get("extension_missing_context")
                            remediation_steps = step_data_res.get("extension_remediation_steps")
                            emotional_sentiment = step_data_res.get("extension_emotional_sentiment")
                            score_val = step_data_res.get("step_4_final_score", 999) if isinstance(step_data_res, dict) else 999

                    _add_ext("justification", "justification", raw_justification, axis_name, score_val)
                    _add_ext("falsification", "falsification", raw_falsification, axis_name, score_val)
                    _add_ext("theory_link", "theory_link", raw_theory_link, axis_name, score_val)
                    _add_ext("risk_flag", "risk_flag", raw_risk_flag, axis_name, score_val)
                    _add_ext("coaching", "coaching", coaching, axis_name, score_val)
                    _add_ext("missing_context", "missing_context", missing_context, axis_name, score_val)
                    _add_ext("remediation_steps", "remediation_steps", remediation_steps, axis_name, score_val)
                    _add_ext("emotional_sentiment", "emotional_sentiment", emotional_sentiment, axis_name, score_val)
                    _add_ext("confidence", "confidence", confidence, axis_name, score_val)

                    # We perform algorithmic extraction of Citations here!

                    if "citation" in visible_extensions and (raw_cited_source_id or raw_cited_text_quote or raw_cited_web_citation):
                        if "citation" not in grouped_extensions:
                            grouped_extensions["citation"] = []
                        
                        citation_hash = str(raw_cited_source_id) + str(raw_cited_text_quote) + str(raw_cited_web_citation)
                        cite_exists = False
                        for existing in grouped_extensions["citation"]:
                            existing_hash = str(existing.get("cited_source_id","")) + str(existing.get("cited_text_quote","")) + str(existing.get("cited_web_citation",""))
                            if existing_hash == citation_hash:
                                if axis_name not in existing["axis_name"]:
                                    existing["axis_name"] += f" & {axis_name}"
                                cite_exists = True
                                break
                        if not cite_exists:
                            grouped_extensions["citation"].append({
                                "axis_name": axis_name,
                                "cited_source_id": raw_cited_source_id,
                                "cited_text_quote": raw_cited_text_quote,
                                "cited_web_citation": raw_cited_web_citation,
                            })

        # Process limit/truncation based on max_extension_items
        for ext_group, items in list(grouped_extensions.items()):
            if max_extension_items is not None and len(items) > max_extension_items:
                # Sort by score ascending (lowest score is most critical)
                items.sort(key=lambda x: getattr(x, "_score", x.get("_score", 999)) if isinstance(x, dict) else getattr(x, "_score", 999))
                grouped_extensions[ext_group] = items[:max_extension_items]
            
            # Clean up the internal _score key (dicts only; Pydantic ignores private attributes)
            for item in grouped_extensions[ext_group]:
                if isinstance(item, dict):
                    item.pop("_score", None)

        layouts_list = []
        # Pre-fetch prompt blocks to enrich axis labels
        # (Blocks already fetched above for global aggregation)

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

        profile_cache = execution.profile_syntheses.get(resolved_pid)
        section_syntheses = {}
        synthesis_md = None
        xai_highlights_cache = []
        if profile_cache:
            section_syntheses = profile_cache.section_syntheses
            synthesis_md = profile_cache.synthesized_markdown
            xai_highlights_cache = getattr(profile_cache, "xai_highlights", [])
            
        # Merge XAI Highlights from cache into grouped_extensions
        for highlight in xai_highlights_cache:
            # Type name should act as the group key, mapping it to SDUI's new box dictionary.
            group_key = highlight.get("type_name", "insight").lower().replace(" ", "_")
            if group_key not in grouped_extensions:
                grouped_extensions[group_key] = []
            
            # Use XAI evidence box definition which XAIExtensionsBox will gracefully parse!
            grouped_extensions[group_key].append(highlight)


        if results.get("has_warning"):
            has_warning = True

        global_score = None
        penalties_applied = []
        if isinstance(scoring_out, dict):
            t_score = scoring_out.get("total_score")
            global_score = float(round(float(t_score), 1)) if t_score is not None else None
            penalties_applied = scoring_out.get("penalties_applied", [])

        try:
            for idx, layout_def in enumerate(layout_defs):
                preset_view = layout_def.preset_view
                target_blocks = layout_def.target_blocks
                # if target_blocks missing, default to empty list. But models say it is guaranteed and non-empty.
                text_delivery_mode = layout_def.text_delivery_mode

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

                                if text_delivery_mode != "none":
                                    if is_legacy_score:
                                        justification = str(step_data.get("justification", ""))
                                    else:
                                        if isinstance(v, dict):
                                            eval_notes = v.get("evaluation_notes", "")
                                            justification = str(v.get("step_3_logical_friction", eval_notes) or "")
                                            cited_source_id = str(v.get("step_1b_cited_source_id", ""))
                                            cited_text_quote = str(v.get("step_1_evidence_quote", ""))
                                            cited_web_citation = str(v.get("step_1c_google_citation", ""))
                                            falsification = v.get("extension_falsification", v.get("step_2_falsification"))
                                            theory_link = v.get("extension_theory_link")
                                            risk_flag = v.get("extension_risk_flag")
                                            coaching = v.get("extension_coaching")
                                            confidence = v.get("extension_confidence")
                                            missing_context = v.get("extension_missing_context")
                                            remediation_steps = v.get("extension_remediation_steps")
                                            emotional_sentiment = v.get("extension_emotional_sentiment")
                                        else:
                                            eval_notes = step_data.get("evaluation_notes", "")
                                            justification = str(step_data.get("step_3_logical_friction", eval_notes) or "")
                                            cited_source_id = str(step_data.get("step_1b_cited_source_id", ""))
                                            cited_text_quote = str(step_data.get("step_1_evidence_quote", ""))
                                            cited_web_citation = str(step_data.get("step_1c_google_citation", ""))
                                            falsification = step_data.get("step_2_falsification")
                                            theory_link = step_data.get("extension_theory_link")
                                            risk_flag = step_data.get("extension_risk_flag")
                                            coaching = step_data.get("extension_coaching")
                                            confidence = step_data.get("extension_confidence")
                                            missing_context = step_data.get("extension_missing_context")
                                            remediation_steps = step_data.get("extension_remediation_steps")
                                            emotional_sentiment = step_data.get("extension_emotional_sentiment")

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
                import bleach

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
            f_context = getattr(execution, "frozen_context", None)
            if f_context:
                raw_audits = f_context.get("mcp_tool_audit", []) if isinstance(f_context, dict) else getattr(f_context, "mcp_tool_audit", [])
                if raw_audits:
                    seen_audits = set()
                    for audit in raw_audits:
                        # Defensive parsing in case elements are Pydantic models vs dicts
                        t_name = getattr(audit, "tool_id", None) or (audit.get("tool_id") if isinstance(audit, dict) else "")
                        t_args = getattr(audit, "query", None) or (audit.get("query") if isinstance(audit, dict) else "")
                        
                        audit_hash = f"{t_name}::{t_args}"
                        if audit_hash not in seen_audits:
                            seen_audits.add(audit_hash)
                            mcp_audit_data.append(audit)

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
                grouped_extensions=grouped_extensions,
                penalties_applied=penalties_applied,
            )
            return dto
        except Exception as e:
            msg = f"Failed to map execution {execution.id} results to ReportDataDTO: {e}"
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED}
            ) from e
