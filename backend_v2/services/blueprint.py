"""Blueprint Transformer Service for V3 Extreme MVC."""

import logging
from typing import Any

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

        results = execution.results or {}
        locale = accept_language or execution.metadata.get("target_locale", "en")

        def _extract_i18n(val: dict | None) -> dict[str, str]:
            """Ensure payload serializes nested I18nText structures into flat dictionaries to pass Pydantic."""
            if val and isinstance(val, dict):
                return val.get("translations", val)
            return {}

        output_profiles = workflow_data.get("output_profiles", {})
        default_profile_id = workflow_data.get("default_profile_id", "default")
        resolved_pid = profile_id if profile_id and profile_id in output_profiles else default_profile_id

        if not output_profiles:
            # Fallback if the database hasn't populated output profiles
            output_profiles = {
                "default": {
                    "name": {"fi": "Oletusraportti", "en": "Default Report"},
                    "layouts": [{"preset_view": "1d_metrics"}]
                }
            }
            resolved_pid = "default"

        available_profiles_map = {}
        for pid, pdef in output_profiles.items():
            name_dict = _extract_i18n(pdef.get("name", {"fi": pid, "en": pid}))
            available_profiles_map[pid] = name_dict.get(locale, name_dict.get("fi", pid))

        profile = output_profiles.get(resolved_pid)
        if not profile:
            msg = f"Profile '{resolved_pid}' not found for workflow '{execution.workflow_id}'."
            logger.error(f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        profile_name = _extract_i18n(profile.get("name", {"fi": "Oletusraportti", "en": "Default Report"}))
        layout_defs = profile.get("layouts", [])

        synthesis = None
        for _step_id, step_data in results.items():
            if isinstance(step_data, dict) and "synthesis" in step_data:
                synthesis = step_data.get("synthesis")
                break

        layouts_list = []
        # Pre-fetch prompt blocks to enrich axis labels
        all_blocks = await self.repo.get_all_prompt_blocks()
        blocks_by_slug = {b["id"]: b for b in all_blocks if "id" in b}

        for layout_def in layout_defs:
            preset_view = layout_def.get("preset_view", "default")
            target_blocks = layout_def.get("target_blocks", [])
            target_steps = layout_def.get("steps", [])
            show_text = layout_def.get("show_text", True)
            
            layout_title = _extract_i18n(layout_def.get("title"))
            layout_desc = _extract_i18n(layout_def.get("description"))

            axes = []
            unsorted_axes = {}
            for step_id, step_data in results.items():
                if target_steps and step_id not in target_steps:
                    continue
                if isinstance(step_data, dict):
                    for k, v in step_data.items():
                        is_legacy_score = (k == "score")
                        suffix_list = ["_justification", "_scaled", "_normalized", "_raw", "_cited_source_id", "_cited_text_quote", "_google_citation"]
                        is_suffix_key = any(k.endswith(sfx) for sfx in suffix_list)

                        if is_legacy_score or (not is_suffix_key and (isinstance(v, (int, float)) or str(v).replace('.', '', 1).isdigit())):
                            try:
                                score_float = float(v)
                            except (ValueError, TypeError):
                                continue
                            
                            axis_name = step_id if is_legacy_score else k
                            axis_description = ""
                            scale_min = 0.0
                            scale_max = 100.0
                            scale_labels = {}

                            block = blocks_by_slug.get(k)
                            if block:
                                label_obj = block.get("label", {})
                                trans_dict = _extract_i18n(label_obj)
                                axis_name = trans_dict.get(locale, trans_dict.get("en", k))

                                desc_obj = block.get("description", {})
                                trans_dict_desc = _extract_i18n(desc_obj)
                                axis_description = trans_dict_desc.get(locale, trans_dict_desc.get("en", ""))

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

                            justification = ""
                            cited_source_id = ""
                            cited_text_quote = ""
                            cited_web_citation = ""

                            if show_text:
                                if is_legacy_score:
                                    justification = step_data.get("justification", "")
                                else:
                                    eval_notes = step_data.get("evaluation_notes", "")
                                    justification = step_data.get(f"{k}_justification", eval_notes)
                                cited_source_id = step_data.get(f"{k}_cited_source_id", "")
                                cited_text_quote = step_data.get(f"{k}_cited_text_quote", "")
                                cited_web_citation = step_data.get(f"{k}_google_citation", "")

                            unsorted_axes[k] = ReportAxisDTO(
                                name=axis_name,
                                description=axis_description,
                                score=score_float,
                                justification=justification,
                                cited_source_id=cited_source_id,
                                cited_text_quote=cited_text_quote,
                                cited_web_citation=cited_web_citation,
                                scale_min=scale_min,
                                scale_max=scale_max,
                                scale_labels=scale_labels
                            )

            if target_blocks:
                for b_id in target_blocks:
                    if b_id in unsorted_axes:
                        axes.append(unsorted_axes[b_id])
            else:
                axes = list(unsorted_axes.values())

            if axes or preset_view == "text_only":
                layouts_list.append(
                    ReportLayoutDTO(
                        preset_view=preset_view,
                        title=layout_title,
                        description=layout_desc,
                        axes=axes,
                        show_text=show_text,
                    )
                )

        org_name = execution.organization_id
        if execution.organization_id:
            try:
                # Need to lookup organisation if possible
                org = await self.repo.get_document("organizations", execution.organization_id)
                if org and "name" in org:
                    org_name = org["name"]
            except Exception:
                pass

        try:
            dto = ReportDataDTO(
                workflow_id=execution.workflow_id,
                profile_id=resolved_pid,
                profile_name=profile_name,
                available_profiles=available_profiles_map,
                created_at=execution.created_at,
                org_name=org_name,
                synthesis=synthesis,
                layouts=layouts_list
            )
            return dto
        except Exception as e:
            msg = f"Failed to map execution {execution.id} results to ReportDataDTO: {e}"
            logger.error(f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED}) from e
