"""Prompt Builder module for standardized Markdown scaffolding.

Ensures strict compliance with the De-Generator Markdown standard by encapsulating
formatting logic, preventing token-heavy XML concatenation bugs.
"""

from __future__ import annotations

import logging
from typing import Final

from backend_v2.exceptions import AppException, ErrorCodes

__all__ = ["build_system_directive"]

logger = logging.getLogger(__name__)

_FORBIDDEN_XML_TAGS: Final[tuple[str, ...]] = (
    "<system_directive>",
    "</system_directive>",
    "<role>",
    "</role>",
    "<objective>",
    "</objective>",
)


def _raise_validation_error(message: str) -> None:
    """Log and raise a Fail-Fast validation AppException.

    Args:
        message: The structural validation failure reason.

    Raises:
        AppException: Always raised with ErrorCodes.VALIDATION_FAILED (HTTP 400).
    """
    logger.error(
        "[PromptBuilder] %s: %s",
        ErrorCodes.VALIDATION_FAILED.name,
        message,
        exc_info=True,
        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )
    raise AppException(
        message=message,
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )


def _validate_no_raw_xml(text: str) -> None:
    """Verify that directive text does not embed forbidden raw XML wrapper tags.

    Args:
        text: The text segment to inspect.

    Raises:
        AppException: Triggered with ErrorCodes.VALIDATION_FAILED if forbidden XML tags exist.
    """
    for tag in _FORBIDDEN_XML_TAGS:
        if tag in text:
            _raise_validation_error(f"Forbidden raw XML directive tag '{tag}' detected in prompt builder.")


def build_system_directive(
    objective: str | None = None,
    rules: list[str] | None = None,
    **kwargs: str | list[str] | None,
) -> str:
    """Build a standardized Markdown system directive for LLMs.

    Args:
        objective: The main objective text under `## Objective`.
        rules: A list of individual rules to be formatted as bullet points under `## Rules`.
        **kwargs: Any additional blocks (e.g. context="...", definitions=["..."])
            which will be formatted as `## Key`. Lists will be joined with newlines.

    Returns:
        A formatted Markdown string containing the requested directive sections.

    Raises:
        AppException: Triggered with ErrorCodes.VALIDATION_FAILED if objective, rules,
            or any keyword block argument violates the expected string/list contract
            or embeds forbidden raw XML directive tags.
    """
    blocks: list[str] = []

    match objective:
        case None:
            pass
        case str():
            _validate_no_raw_xml(objective)
            if objective.strip():
                blocks.append(f"## Objective\n{objective.strip()}")
        case _:
            _raise_validation_error("Objective must be a string or None.")

    for key, value in kwargs.items():
        match value:
            case None:
                continue
            case str():
                _validate_no_raw_xml(value)
                value_str = value.strip()
                if value_str:
                    title = key.replace("_", " ").title()
                    blocks.append(f"## {title}\n{value_str}")
            case list() if all(isinstance(v, str) for v in value):
                for item in value:
                    _validate_no_raw_xml(item)
                cleaned_items = [f"- {v.strip()}" for v in value if v.strip()]
                if cleaned_items:
                    title = key.replace("_", " ").title()
                    value_str = "\n".join(cleaned_items)
                    blocks.append(f"## {title}\n{value_str}")
            case _:
                _raise_validation_error(f"Keyword block '{key}' must be a string, list of strings, or None.")

    match rules:
        case None:
            pass
        case list() if all(isinstance(r, str) for r in rules):
            for rule_item in rules:
                _validate_no_raw_xml(rule_item)
            cleaned_rules = [f"- {r.strip()}" for r in rules if r.strip()]
            if cleaned_rules:
                rules_md = "\n".join(cleaned_rules)
                blocks.append(f"## Rules\n{rules_md}")
        case _:
            _raise_validation_error("Rules must be a list of strings or None.")

    if not blocks:
        return ""

    return "\n\n".join(blocks)
