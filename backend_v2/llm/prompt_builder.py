"""Prompt Builder module for standardized XML scaffolding.

Ensures strict compliance with Rule 51 (Hybrid XML Prompting) by encapsulating
XML generation logic, preventing malformed tags and string concatenation bugs.
"""


def build_system_directive(
    objective: str | None = None,
    rules: list[str] | None = None,
    **kwargs: str | list[str],
) -> str:
    """Builds a standardized XML system directive for LLMs.

    Args:
        objective: The main objective text inside <objective>.
        rules: A list of individual rules to be wrapped in <rules><rule>...</rule></rules>.
        **kwargs: Any additional XML blocks (e.g. context="...", definitions=["..."])
                  which will be formatted as <key>value</key>. Lists will be joined with newlines.

    Returns:
        A perfectly formatted XML string.

    Raises:
        None: This function does not raise any exceptions and handles empty inputs
            by returning an empty system directive tag.
    """
    blocks = []

    if objective:
        blocks.append(f"  <objective>\n{objective.strip()}\n  </objective>")

    # Add any extra blocks passed via kwargs (e.g. context="xyz")
    for key, value in kwargs.items():
        if value:
            # Handle list arguments for kwargs by joining them with newlines
            if isinstance(value, list):
                value = "\n".join(str(v).strip() for v in value)
            blocks.append(f"  <{key}>\n{str(value).strip()}\n  </{key}>")

    if rules:
        rules_xml = "\n".join(f"    <rule>{r.strip()}</rule>" for r in rules)
        blocks.append(f"  <rules>\n{rules_xml}\n  </rules>")

    if not blocks:
        return "<system_directive>\n</system_directive>"

    blocks_str = "\n".join(blocks)
    return f"<system_directive>\n{blocks_str}\n</system_directive>"
