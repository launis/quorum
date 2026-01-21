"""Matrix Formatter Service for Evaluation Matrices."""

import json
from typing import Any


def format_matrix_component(component: dict[str, Any]) -> str:
    """Formats a JSON-based Evaluation Matrix into a human-readable prompt string.

    Args:
        component (dict): The matrix component structure.

    Returns:
        str: The formatted string.
    """
    content = component.get("content", {})
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except Exception:
            return "Error parsing matrix."

    name = content.get("name", "Audit Matrix")
    desc = content.get("description", "")
    role = content.get("role_description", "You are the Evaluator.")
    criteria = content.get("criteria", [])
    scale = content.get("scale")
    if not scale:
        raise ValueError(f"Matrix component '{name}' is missing required 'scale' configuration.")
    
    if "min" not in scale or "max" not in scale:
        raise ValueError(f"Matrix component '{name}' scale definition is incomplete. Requires 'min' and 'max'.")

    scale_min = int(scale["min"])
    scale_max = int(scale["max"])

    if scale_min >= scale_max:
        raise ValueError(f"Matrix component '{name}' scale invalid: min ({scale_min}) must be strictly less than max ({scale_max}).")

    prompt_lines = [
        f"### ROLE: {role}",
        f"### EVALUATION MATRIX: {name}",
        f"Description: {desc}",
        f"Scale: {scale_min}-{scale_max}",
        "",
        "### CRITERIA FOR EVALUATION:",
    ]

    for crit in criteria:
        c_label = crit.get("label", "Unknown")
        c_instr = crit.get("instruction", "")
        c_id = crit.get("id", "unknown")
        c_anchors = crit.get("anchors", {})

        prompt_lines.append(f"#### Dimension: {c_label} (ID: {c_id})")
        prompt_lines.append(f"Instruction: {c_instr}")
        prompt_lines.append("Proficiency Levels (Anchors):")
        try:
            sorted_anchors = sorted(c_anchors.items(), key=lambda x: int(x[0]))
        except Exception:
            sorted_anchors = c_anchors.items()

        # Dynamic Scale Injection Logic
        anchor_min = 1
        anchor_max = 4
        if sorted_anchors:
            try:
                anchor_indices = [int(k) for k, v in sorted_anchors]
                anchor_min = min(anchor_indices)
                anchor_max = max(anchor_indices)
            except Exception:
                pass

        for lvl, text in sorted_anchors:
            prompt_lines.append(f"  - Level {lvl}: {text}")
        
        # Inject explicit mapping instruction if scale differs from anchors
        if scale_min != anchor_min or scale_max != anchor_max:
             prompt_lines.append(f"  [SCORING INSTRUCTION]: Map the Anchor Levels ({anchor_min}-{anchor_max}) to the required Scale ({scale_min}-{scale_max}).")
             prompt_lines.append(f"  - Anchor Level {anchor_min} corresponds to Score {scale_min}.")
             prompt_lines.append(f"  - Anchor Level {anchor_max} corresponds to Score {scale_max}.")
             
             # Conditional Instructions
             scale_range = scale_max - scale_min
             
             if scale_range > 0:
                 prompt_lines.append(f"  - Use the FULL SCALE ({scale_min}-{scale_max}) to reflect nuance. Do NOT limit scores to just the mapped anchor points.")
             
             if scale_range > 10:
                 prompt_lines.append(f"    * Example: A score of {(scale_min + scale_max * 3)//4} is valid if the performance is between Level 3 and Level 4.")
                 prompt_lines.append(f"    * Precision Principle: The larger the scale, the more precise the evaluation must be.")
             
             if scale_range > 1:
                 prompt_lines.append("  - Interpolate values linearly for levels in between.")
             else:
                 prompt_lines.append("  - This is a BINARY scale. Choosing intermediate anchors implies a choice between Min and Max.")

        prompt_lines.append("")

    return "\n".join(prompt_lines)
