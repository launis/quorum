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
    scale = content.get("scale", {"min": 1, "max": 4})

    prompt_lines = [
        f"### ROLE: {role}",
        f"### EVALUATION MATRIX: {name}",
        f"Description: {desc}",
        f"Scale: {scale.get('min')}-{scale.get('max')}",
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

        for lvl, text in sorted_anchors:
            prompt_lines.append(f"  - Level {lvl}: {text}")
        prompt_lines.append("")

    return "\n".join(prompt_lines)
