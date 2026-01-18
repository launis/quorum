"""Security hooks for PII redaction and keyword banning."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.state import WorkflowState
from backend.exceptions import SecurityViolationError

logger = logging.getLogger(__name__)

# Define Regex patterns for PII
PII_PATTERNS = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "PHONE_FI": r"\b(?:\+358|0)[\s-]?\d{2,3}[\s-]?\d{3,4}[\s-]?\d{3,4}\b",
    "HETU": r"\b\d{6}[+A-]\d{3}[0-9A-Z]\b",  # Finnish SSN
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}


def sanitize_text(text: str) -> tuple[str, list[str]]:
    """Sanitizes text by removing potential PII patterns.

    This is a basic regex-based filter. For production, use a dedicated DLP service.
    based on predefined Regex patterns (e.g. Email, SSN, Credit Card).

    Args:
        text (str): Input text to sanitize.

    Returns:
        Tuple[str, List[str]]: A tuple containing:
            1. The sanitized text with PII replaced by [REDACTED_TYPE].
            2. A list of strings describing what was detected/redacted (e.g. "EMAIL: 2 items").

    """
    if not text:
        return text, []

    threats_detected = []
    # 1. Normalize Unicode (Basic)
    clean_value = "".join(ch for ch in text if ch.isprintable())

    # 2. Robust PII Redaction
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, clean_value)
        if matches:
            distinct_matches = list(set(matches))
            threats_detected.append(f"{pii_type}: {len(distinct_matches)} items")

            # Redact
            clean_value = re.sub(pattern, f"[REDACTED_{pii_type}]", clean_value)

    return clean_value, threats_detected


def check_banned_phrases(text: str, phrases: list[str]) -> list[str]:
    """Checks if the input text contains any of the specified banned phrases (case-insensitive).

    Args:
        text (str): The text to scan.
        phrases (List[str]): List of banned phrases or keywords.

    Returns:
        List[str]: A list of unique banned phrases found in the text.

    """
    if not text or not phrases:
        return []

    detected = []
    text_lower = text.lower()
    for phrase in phrases:
        if phrase.lower() in text_lower:
            detected.append(phrase)

    return list(set(detected))


# --- WORKFLOW STATE WRAPPERS (for HOOK_MAPPING compatibility) ---

# NOTE (Jan 2026): Removed DEFAULT_BANNED_PHRASES per Zero-Fallback Rule.
# Banned phrases MUST be fetched from database.


def sanitize_text_hook(state) -> WorkflowState:
    """WorkflowState wrapper for sanitize_text.

    Sanitizes all text inputs and stores results in aux_data.
    """
    logger.debug("[SecurityHook] Running sanitize_text_hook...")

    if not hasattr(state, "inputs") or not state.inputs:
        return state

    sanitized_inputs = {}
    threats_summary = []

    for field in ["history_text", "product_text", "reflection_text"]:
        original = getattr(state.inputs, field, "") or ""
        if original.strip():
            sanitized, threats = sanitize_text(original)
            sanitized_inputs[field] = sanitized
            if threats:
                threats_summary.extend(threats)
        else:
            sanitized_inputs[field] = original

    state.aux_data["sanitized_inputs"] = sanitized_inputs
    state.aux_data["pii_threats_detected"] = threats_summary

    if threats_summary:
        logger.warning(f"[SecurityHook] PII detected and redacted: {threats_summary}")
    else:
        logger.debug("[SecurityHook] No PII detected.")

    return state


async def check_banned_phrases_hook(state, repository=None) -> WorkflowState:
    """WorkflowState wrapper for check_banned_phrases.

    Scans all text inputs for banned phrases fetched from database.

    NOTE: This hook requires repository parameter to fetch banned phrases.
    Falls back to empty list if repository not provided (Zero-Fallback compliance).
    """
    logger.debug("[SecurityHook] Running check_banned_phrases_hook...")

    if not hasattr(state, "inputs") or not state.inputs:
        return state

    # Fetch banned phrases from database (Zero-Fallback compliance)
    banned_phrases = []
    if repository:
        try:
            phrases_records = await repository.get_banned_phrases()
            banned_phrases = [p.get("phrase", "") for p in phrases_records if p.get("phrase")]
            logger.debug(f"[SecurityHook] Loaded {len(banned_phrases)} banned phrases from DB.")
        except Exception as e:
            logger.error(f"[SecurityHook] Failed to fetch banned phrases: {e}")
            # Zero-Fallback: Fail explicitly, don't use hardcoded defaults
            state.aux_data["banned_phrases_error"] = str(e)
            return state
    else:
        logger.warning("[SecurityHook] No repository provided - skipping banned phrase check.")
        state.aux_data["banned_phrases_detected"] = []
        return state

    all_text = ""
    for field in ["history_text", "product_text", "reflection_text"]:
        text = getattr(state.inputs, field, "") or ""
        all_text += text + "\n"

    detected = check_banned_phrases(all_text, banned_phrases)

    state.aux_data["banned_phrases_detected"] = detected

    if detected:
        msg = f"[SecurityHook] Banned phrases detected: {detected}"
        logger.error(msg)
        raise SecurityViolationError(msg, details={"banned_phrases": detected})
    else:
        logger.debug("[SecurityHook] No banned phrases detected.")

    return state
