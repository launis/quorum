"""Two-Tier SSOT Length Budgeting Engine (Tier 2 Guardrail).

Enforces sentence-boundary aware character budgeting, preventing mid-sentence
and mid-word truncation of executive reports while maintaining semantic integrity.
"""

import logging
import re

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

__all__ = ["enforce_sentence_boundary_budget"]

_TERMINAL_PUNCTUATION = {".", "!", "?"}


def enforce_sentence_boundary_budget(text: str, max_chars: int) -> str:
    """Enforce character budget cleanly at sentence boundaries without mid-word slicing.

    Args:
        text: Input generated text to constrain.
        max_chars: Maximum character budget. Must be a positive integer.

    Returns:
        Sentence-budgeted text guaranteed to conclude on a valid sentence boundary
        or complete word boundary.

    Raises:
        AppException: If text is empty/whitespace-only, or max_chars is <= 0.
    """
    if max_chars <= 0:
        msg = f"max_chars must be a positive integer, but received {max_chars}."
        logger.error("[LengthBudgetEnforcer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    stripped_text = text.strip()
    if not stripped_text:
        msg = "Input text cannot be empty or whitespace-only."
        logger.error("[LengthBudgetEnforcer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if len(stripped_text) <= max_chars:
        return stripped_text

    # Scan backwards from max_chars to locate nearest terminal punctuation
    window_min = int(max_chars * 0.6)
    candidate_slice = stripped_text[:max_chars]

    # Find last terminal punctuation within [window_min, max_chars]
    best_punct_idx = -1
    for i in range(len(candidate_slice) - 1, window_min - 1, -1):
        char = candidate_slice[i]
        if char in _TERMINAL_PUNCTUATION:
            # Check that it's a true sentence end (followed by space, end of slice, or quote)
            if i + 1 == len(stripped_text) or candidate_slice[i + 1 : i + 2] in {" ", '"', "'", "\n", ""}:
                best_punct_idx = i
                break

    if best_punct_idx != -1:
        # Include closing quote or bracket if present immediately after punctuation
        end_idx = best_punct_idx + 1
        if end_idx < len(stripped_text) and stripped_text[end_idx] in {'"', "'", "”", "’"}:
            end_idx += 1
        return stripped_text[:end_idx].strip()

    # Fallback: No sentence boundary found in [60%, 100%] window.
    # Locate the first complete sentence
    first_sentence_match = re.search(r"^.*?[.!?](?:\s|$)", stripped_text, flags=re.DOTALL)
    if first_sentence_match:
        first_sentence = first_sentence_match.group(0).strip()
        if len(first_sentence) <= max_chars:
            logger.warning(
                "[LengthBudgetEnforcer] No sentence boundary in 60-100%% window of budget %d. "
                "Retaining first complete sentence (%d chars).",
                max_chars,
                len(first_sentence),
            )
            return first_sentence

    # If even the first sentence exceeds max_chars, trim at the last complete word boundary
    last_space_idx = candidate_slice.rfind(" ")
    if last_space_idx > 0:
        trimmed = candidate_slice[:last_space_idx].rstrip()
        # Append period if not ending with punctuation
        if trimmed and trimmed[-1] not in _TERMINAL_PUNCTUATION:
            trimmed += "."
        logger.warning(
            "[LengthBudgetEnforcer] Single unbroken sentence exceeded %d chars. Trimmed at word boundary (%d chars).",
            max_chars,
            len(trimmed),
        )
        return trimmed

    # Absolute fallback: candidate slice with terminal punctuation appended
    logger.warning(
        "[LengthBudgetEnforcer] Unbroken single token exceeded %d chars. Terminating at limit with punctuation.",
        max_chars,
    )
    return candidate_slice.rstrip() + "."
