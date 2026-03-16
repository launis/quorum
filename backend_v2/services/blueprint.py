"""Blueprint Transformer Service for V6.0 Dynamic SDUI."""

import logging
from typing import Any

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import RenderBlueprint

logger = logging.getLogger(__name__)

class BlueprintTransformer:
    """The Universal Transformer Hub. Merges Execution Data with SDUI Blueprints."""

    def __init__(self, repo: AbstractWorkflowRepository):
        self.repo = repo

    async def build_render_payload(self, execution_id: str, accept_language: str | None = None) -> dict[str, Any]:
        """Builds the localized rendering payload by merging results with the blueprint.
        Implements Late-Binding Localization (Layer 5) and Graceful Degradation.
        """
        execution = await self.repo.get_execution(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found."
            logger.error(f"[BlueprintTransformer] {ErrorCodes.RESOURCE_NOT_FOUND.name}: {msg}")
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND}
            )

        if not execution.render_blueprints or "default" not in execution.render_blueprints:
            msg = f"Execution {execution_id} is missing render_blueprints['default']."
            logger.error(f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED}
            )

        # Validate blueprint structure
        try:
            blueprint = RenderBlueprint.model_validate(execution.render_blueprints["default"])
        except Exception as e:
            msg = f"Invalid render_blueprint structure in Execution {execution_id}: {e}"
            logger.error(f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED}
            ) from e

        # Determine locale
        locale = accept_language or execution.metadata.get("target_locale", "en")

        # Fetch blocks for late-binding translations
        all_blocks = await self.repo.get_all_prompt_blocks()
        blocks_by_slug = {b["id"]: b for b in all_blocks if "id" in b}

        results = execution.results or {}

        def resolve_data_path(path: str) -> Any:
            """Safe dot-notation lookup with Graceful Degradation logging."""
            parts = path.lstrip("$").split(".")
            current = {"results": results}
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    msg = f"Missing data at path {path} in execution {execution_id}"
                    logger.warning(f"[BlueprintTransformer] VALIDATION_FAILED: {msg}")
                    return None
            return current

        def get_translation(translation_dict: dict[str, str], fallback: str = "en") -> str:
            """Extract translated term adhering to layer 5 translation schema doctrine."""
            if not translation_dict:
                return ""
            return translation_dict.get(locale, translation_dict.get(fallback, ""))

        # 6.3 Graceful Degradation logging helper
        def safe_float_cast(raw_value: Any, key_path: str) -> float | None:
            if raw_value is None:
                return None
            try:
                return float(raw_value)
            except (ValueError, TypeError):
                logger.error(
                    f"[BlueprintTransformer] {ErrorCodes.VALIDATION_FAILED.name}: "
                    f"LLM returned Corrupted/Non-numeric data for path '{key_path}', "
                    f"Gracefully Skipping Component rendering. Value: {raw_value}",
                    exc_info=True
                )
                return None

        def get_scale_text(value: float | None, data_path: str) -> str:
            """Resolves the textual scale name (e.g., 'CATASTROPHIC FAILURE') for a given matrix score."""
            if value is None or not data_path:
                return ""

            slug = data_path.split(".")[-1]
            block = blocks_by_slug.get(slug)
            if not block or "scales" not in block:
                return ""

            rounded_val = round(value)
            for scale in block["scales"]:
                if scale.get("score") == rounded_val:
                    name_obj = scale.get("name")
                    if isinstance(name_obj, dict):
                        return get_translation(name_obj.get("translations", {}), name_obj.get("default_locale", "en"))
                    elif isinstance(name_obj, str):
                        return name_obj
            return ""

        def get_scale_max(data_path: str, default_max: float = 6.0) -> float:
            """Resolves the maximum scale strictly from the block's scales array."""
            if not data_path:
                return default_max
            slug = data_path.split(".")[-1]
            # Handle normalized max values explicitly if the path ends with _normalized
            if slug.endswith("_normalized"):
                return 100.0

            # If the slug ends with _scaled, we can look up the base slug
            if slug.endswith("_scaled"):
                slug = slug.replace("_scaled", "")

            block = blocks_by_slug.get(slug)
            if block:
                # Dynamically calculate from scales array ALWAYS (scale_max/scale_min in json are for other uses)
                if "scales" in block and isinstance(block["scales"], list):
                    scores = []
                    for scale in block["scales"]:
                        if "score" in scale:
                            try:
                                scores.append(float(scale["score"]))
                            except (ValueError, TypeError):
                                pass
                    if scores:
                        return float(max(scores))

            return default_max

        def get_block_title(data_path: str) -> str:
            """Resolves the localized name of the block itself (e.g., 'Toulminin Argumentaatio')."""
            if not data_path:
                return ""
            slug = data_path.split(".")[-1]
            if slug.endswith("_normalized"):
                 slug = slug.replace("_normalized", "")
            if slug.endswith("_scaled"):
                 slug = slug.replace("_scaled", "")

            block = blocks_by_slug.get(slug)
            if block and "label" in block:
                label_obj = block["label"]
                if isinstance(label_obj, dict):
                    return get_translation(label_obj.get("translations", {}), label_obj.get("default_locale", "en"))
                elif isinstance(label_obj, str):
                    return label_obj
            # Fallback to just the raw slug if no translation available
            return slug

        rendered_components = []

        for comp in blueprint.components:
            base_dict = comp.model_dump(mode="json")
            comp_type = base_dict["type"]

            if comp_type == "header":
                rendered_components.append(base_dict)
            elif comp_type == "metadata_header":
                rendered_components.append(base_dict)
            elif comp_type == "bibliography_footer":
                rendered_components.append(base_dict)
            elif comp_type == "1d_gauge":
                val = resolve_data_path(base_dict["data_path"])
                base_dict["value"] = safe_float_cast(val, base_dict["data_path"])
                if "data_path" in base_dict:
                    base_dict["scale_text"] = get_scale_text(base_dict["value"], base_dict["data_path"])
                    base_dict["scale_max"] = get_scale_max(base_dict["data_path"])
                    # Use provided title from DB if it exists, otherwise resolve it from block translations
                    if "title" not in base_dict or not base_dict["title"]:
                        base_dict["title"] = get_block_title(base_dict["data_path"])
                rendered_components.append(base_dict)
            elif comp_type == "2d_matrix":
                x_val = resolve_data_path(base_dict["x_data_path"])
                y_val = resolve_data_path(base_dict["y_data_path"])

                base_dict["x_value"] = safe_float_cast(x_val, base_dict["x_data_path"])
                base_dict["y_value"] = safe_float_cast(y_val, base_dict["y_data_path"])

                if "x_data_path" in base_dict:
                    base_dict["x_scale_text"] = get_scale_text(base_dict["x_value"], base_dict["x_data_path"])
                    base_dict["x_scale_max"] = get_scale_max(base_dict["x_data_path"])
                    base_dict["x_title"] = get_block_title(base_dict["x_data_path"])
                else:
                    base_dict["x_title"] = ""

                if "y_data_path" in base_dict:
                    base_dict["y_scale_text"] = get_scale_text(base_dict["y_value"], base_dict["y_data_path"])
                    base_dict["y_scale_max"] = get_scale_max(base_dict["y_data_path"])
                    base_dict["y_title"] = get_block_title(base_dict["y_data_path"])
                else:
                    base_dict["y_title"] = ""

                if base_dict.get("x_axis_note"):
                    base_dict["x_note_text"] = resolve_data_path(base_dict["x_axis_note"])
                if base_dict.get("y_axis_note"):
                    base_dict["y_note_text"] = resolve_data_path(base_dict["y_axis_note"])

                rendered_components.append(base_dict)
            elif comp_type == "3d_scatter":
                x_val = resolve_data_path(base_dict["x_data_path"])
                y_val = resolve_data_path(base_dict["y_data_path"])
                z_val = resolve_data_path(base_dict["z_data_path"])

                base_dict["x_value"] = safe_float_cast(x_val, base_dict["x_data_path"])
                base_dict["y_value"] = safe_float_cast(y_val, base_dict["y_data_path"])
                base_dict["z_value"] = safe_float_cast(z_val, base_dict["z_data_path"])

                if "x_data_path" in base_dict:
                    base_dict["x_scale_text"] = get_scale_text(base_dict["x_value"], base_dict["x_data_path"])
                    base_dict["x_scale_max"] = get_scale_max(base_dict["x_data_path"])
                    base_dict["x_title"] = get_block_title(base_dict["x_data_path"])
                else:
                    base_dict["x_title"] = ""

                if "y_data_path" in base_dict:
                    base_dict["y_scale_text"] = get_scale_text(base_dict["y_value"], base_dict["y_data_path"])
                    base_dict["y_scale_max"] = get_scale_max(base_dict["y_data_path"])
                    base_dict["y_title"] = get_block_title(base_dict["y_data_path"])
                else:
                    base_dict["y_title"] = ""

                if "z_data_path" in base_dict:
                    base_dict["z_scale_text"] = get_scale_text(base_dict["z_value"], base_dict["z_data_path"])
                    base_dict["z_scale_max"] = get_scale_max(base_dict["z_data_path"], default_max=100.0)
                    base_dict["z_title"] = get_block_title(base_dict["z_data_path"])
                else:
                    base_dict["z_title"] = ""

                if base_dict.get("x_axis_note"):
                    base_dict["x_note_text"] = resolve_data_path(base_dict["x_axis_note"])
                if base_dict.get("y_axis_note"):
                    base_dict["y_note_text"] = resolve_data_path(base_dict["y_axis_note"])
                if base_dict.get("z_axis_note"):
                    base_dict["z_note_text"] = resolve_data_path(base_dict["z_axis_note"])

                rendered_components.append(base_dict)
            elif comp_type == "evaluation_notes_panel":
                resolved_notes = {}
                for rp in base_dict["data_paths"]:
                    resolved_notes[rp] = resolve_data_path(rp)
                base_dict["resolved_notes"] = resolved_notes
                rendered_components.append(base_dict)
            else:
                rendered_components.append(base_dict)

        payload = {
            "execution_id": execution_id,
            "status": execution.status.value,
            "target_locale": locale,
            "metadata": execution.metadata,
            "blueprint": {
                "version": blueprint.version,
                "components": rendered_components
            }
        }

        # Global Bibliography Aggregation
        biblio = []
        def _scan_for_citations(obj: Any):
             if isinstance(obj, dict):
                 if "citation_reference" in obj and obj["citation_reference"]:
                      biblio.append(obj["citation_reference"])
                 for k, v in obj.items():
                      _scan_for_citations(v)
             elif isinstance(obj, list):
                 for item in obj:
                      _scan_for_citations(item)

        _scan_for_citations(results)
        payload["bibliography"] = list(set(biblio))

        return payload
