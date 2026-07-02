"""Prompt Builder module for standardized Markdown scaffolding.

Ensures strict compliance with the De-Generator Markdown standard by encapsulating
formatting logic, preventing token-heavy XML concatenation bugs.
"""


def build_system_directive(
    objective: str | None = None,
    rules: list[str] | None = None,
    **kwargs: str | list[str],
) -> str:
    """Builds a standardized Markdown system directive for LLMs.

    Args:
        objective: The main objective text under `## Objective`.
        rules: A list of individual rules to be formatted as bullet points under `## Rules`.
        **kwargs: Any additional blocks (e.g. context="...", definitions=["..."])
                  which will be formatted as `## Key`. Lists will be joined with newlines.

    Returns:
        A perfectly formatted Markdown string.
    """
    blocks = []

    if objective:
        blocks.append(f"## Objective\n{objective.strip()}")

    # Add any extra blocks passed via kwargs (e.g. context="xyz")
    for key, value in kwargs.items():
        if value:
            title = key.replace("_", " ").title()
            # Handle list arguments for kwargs by joining them with newlines
            if isinstance(value, list):
                value_str = "\n".join(f"- {str(v).strip()}" for v in value)
            else:
                value_str = str(value).strip()
            blocks.append(f"## {title}\n{value_str}")

    if rules:
        rules_md = "\n".join(f"- {r.strip()}" for r in rules)
        blocks.append(f"## Rules\n{rules_md}")

    if not blocks:
        return ""

    return "\n\n".join(blocks)
