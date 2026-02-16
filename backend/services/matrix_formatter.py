"""Matrix Formatter Service for Evaluation Matrices."""

import json
from typing import Any
from backend.exceptions import AppException, ErrorCodes

def format_matrix_component(component: dict[str, Any]) -> str:
    """Formats a JSON-based Evaluation Matrix into a human-readable prompt string.

    Args:
        component (dict): The matrix component structure.

    Returns:
        str: The formatted string.

    Raises:
        AppException: If configuration is invalid (Fail Fast).
    """
    content = component.get("content", {})
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except Exception as e:
            raise AppException(
                message="Failed to parse matrix content JSON.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)}
            ) from e

    # STRICT MODE: No legacy support. Metadata MUST be at the component root.
    name = component.get("name")
    if not name:
        raise AppException(
            message="Matrix component is missing root-level 'name'.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
        )

    desc = component.get("description", "")
    role = content.get("role_description", "You are the Evaluator.")
    criteria = content.get("criteria", [])
    scale = content.get("scale")
    if not scale:
        raise AppException(
            message=f"Matrix component '{name}' is missing required 'scale' configuration.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
        )

    if "min" not in scale or "max" not in scale:
        raise AppException(
            message=f"Matrix component '{name}' scale definition is incomplete.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
        )

    try:
        scale_min = int(scale["min"])
        scale_max = int(scale["max"])
    except ValueError as e:
         raise AppException(
            message=f"Matrix component '{name}' scale values must be integers.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)}
        ) from e

    if scale_min >= scale_max:
         raise AppException(
            message=f"Matrix component '{name}' scale invalid: min ({scale_min}) >= max ({scale_max}).",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
        )

    prompt_lines = [
        f"### ROLE: {role}",
        f"### EVALUATION MATRIX: {name}",
        f"Description: {desc}",
        f"Scale: {scale_min}-{scale_max}",
    ]

    prompt_lines.append("")
    prompt_lines.append("### CRITERIA FOR EVALUATION:")

    for crit in criteria:
        c_label = crit.get("label", "Unknown")
        c_instr = crit.get("instruction", "")
        c_id = crit.get("id", "unknown")
        c_anchors = crit.get("anchors", {})

        prompt_lines.append(f"#### Dimension: {c_label} (ID: {c_id})")
        prompt_lines.append(f"**JSON Requirement**: You MUST use the exact ID '{c_id}' as the value for 'dimension_id' in your output.")
        prompt_lines.append(f"Instruction: {c_instr}")
        prompt_lines.append("Proficiency Levels (Anchors):")
        
        try:
            sorted_anchors = sorted(c_anchors.items(), key=lambda x: int(x[0]))
        except Exception as e:
             # Fail fast if anchors contain invalid keys (non-integers)
             raise AppException(
                message=f"Invalid anchor keys in matrix '{name}'. Keys must be integers.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)}
            ) from e

        # Dynamic Scale Injection Logic
        anchor_min = 1
        anchor_max = 4
        if sorted_anchors:
            try:
                anchor_indices = [int(k) for k, v in sorted_anchors]
                anchor_min = min(anchor_indices)
                anchor_max = max(anchor_indices)
            except Exception as e:
                 raise AppException(
                    message=f"Failed to calculate anchor range for '{name}'.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)}
                ) from e

        for lvl, text in sorted_anchors:
            prompt_lines.append(f"  - Level {lvl}: {text}")

         # Inject explicit mapping instruction if scale differs from anchors
        if scale_min != anchor_min or scale_max != anchor_max:
             prompt_lines.append(f"  [PISTEYTYSOHJE]: Käytä Ankkuritasoja ({anchor_min}-{anchor_max}) vain LAADULLISINA KIINTOPISTEINÄ.")
             prompt_lines.append(f"  - Asteikko on {scale_min}-{scale_max}.")
             prompt_lines.append(f"  - Suoritus, joka vastaa 'Tasoa {anchor_min}', implikoi pisteitä lähellä arvoa {scale_min}.")
             prompt_lines.append(f"  - Suoritus, joka vastaa 'Tasoa {anchor_max}', implikoi pisteitä lähellä arvoa {scale_max}.")

             # Conditional Instructions
             scale_range = scale_max - scale_min

             if scale_range > 0:
                 prompt_lines.append(f"  - Käytä KOKO ASTEIKKOA ({scale_min}-{scale_max}) kuvastaaksesi nyansseja. ÄLÄ rajoitu vain ankkuripisteisiin.")

             if scale_range > 10:
                 prompt_lines.append(f"    * Esimerkki: Pisteet {(scale_min + scale_max * 3)//4} ovat validit, jos suoritus on Tason 3 ja Tason 4 välissä.")
                 prompt_lines.append("    * Tarkkuusperiaate: Mitä laajempi asteikko, sitä tarkempaa arviointia vaaditaan.")

             if scale_range > 1:
                 prompt_lines.append("  - Interpoloi vapaasti kiintopisteiden välillä ansioiden mukaan.")
             else:
                 prompt_lines.append("  - Tämä on BINÄÄRINEN asteikko. Valitse Min tai Max.")

        prompt_lines.append("")

    return "\n".join(prompt_lines)
