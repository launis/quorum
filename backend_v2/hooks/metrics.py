"""Metrics hooks for calculating text statistics and control ratios."""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


def analyze_text(text: str) -> Any:
    """Calculates objective text metrics from the input text using simple heuristic counting.

    Metrics include word count, sentence count, avg sentence length, lexical diversity,
    and capitalization ratio.

    Args:
        text (str): The raw input text.

    Returns:
        TextMetrics: Key metrics object.

    """
    if not text or not text.strip():
        return {
            "word_count": 0,
            "sentence_count": 0,
            "avg_sentence_length": 0.0,
            "lexical_diversity": 0.0,
            "capitalization_ratio": 0.0,
            "control_ratio": 0.0,
        }

    # 1. Word Count
    words = re.findall(r"\b\w+\b", text.lower())
    word_count = len(words)

    # 2. Sentence Count
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    sentence_count = len(sentences)

    # 3. Averages
    avg_sent_len = word_count / sentence_count if sentence_count > 0 else 0

    # 4. Diversity
    unique_words = set(words)
    lex_diversity = len(unique_words) / word_count if word_count > 0 else 0

    # 5. Caps
    caps = sum(1 for c in text if c.isupper())
    total_chars = sum(1 for c in text if c.isalpha())
    cap_ratio = caps / total_chars if total_chars > 0 else 0

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_sent_len, 2),
        "lexical_diversity": round(lex_diversity, 2),
        "capitalization_ratio": round(cap_ratio, 2),
        "control_ratio": 0.0,  # Default, calculated separately in hook or explicit call
    }


def calculate_control_ratio(text: str) -> float:
    """Calculates ratio of Human Tokens vs Total Tokens (approximation using characters).

    Attempts to parse chat logs based on common headers (User:/AI:).

    Formula: UserChars / (UserChars + AIChars)

    Args:
        text (str): The conversation history or transcript.

    Returns:
        float: Control ratio between 0.0 (Pure AI) and 1.0 (Pure Human).

    """
    if not text:
        return 0.0

    user_chars = 0
    ai_chars = 0

    # Normalize to lines
    lines = text.split("\n")
    current_speaker = "user"  # Default to 'user' for single unheadered prompts

    user_headers = ["user:", "human:", "k:", "käyttäjä:", "me:", "minä:"]
    ai_headers = ["ai:", "assistant:", "t:", "tekoäly:", "gpt:", "bot:"]

    for line in lines:
        lower_line = line.strip().lower()

        # Check for header switch
        started_new_block = False
        for h in user_headers:
            if lower_line.startswith(h):
                current_speaker = "user"
                line_content = line[len(h) :]
                user_chars += len(line_content.strip())
                started_new_block = True
                break

        if not started_new_block:
            for h in ai_headers:
                if lower_line.startswith(h):
                    current_speaker = "ai"
                    line_content = line[len(h) :]
                    ai_chars += len(line_content.strip())
                    started_new_block = True
                    break

        # If continuation of previous block
        if not started_new_block and current_speaker:
            clean_len = len(line.strip())
            if current_speaker == "user":
                user_chars += clean_len
            else:
                ai_chars += clean_len

    total_chars = user_chars + ai_chars
    if total_chars == 0:
        return 0.0

    return round(user_chars / total_chars, 4)


def calculate_behavioral_metrics(metrics: Any) -> Any:
    """Calculates heuristic behavioral metrics (Say-Do Gap, Automation Bias).

    NOTE: These are heuristic approximations to serve as a 'Single Source of Truth'
    alongside the LLM's qualitative analysis.
    """
    say_do_gap = 0.0
    automation_bias = 0.0
    illusion_of_competence = 0.0
    imperative_command_count = 0

    if not metrics:
        return {
            "say_do_gap": say_do_gap,
            "automation_bias": automation_bias,
            "illusion_of_competence": illusion_of_competence,
            "imperative_command_count": imperative_command_count,
        }

    # 1. Automation Bias (Heuristic: Short, affirmative user messages)
    # If user messages are consistently short (< 5 words) and frequent.
    user_lines: list[str] = []

    if user_lines:
        short_responses = 0
        for line in user_lines:
            if len(line.split()) < get_settings().metrics_short_response_word_count:
                short_responses += 1

        if len(user_lines) > 2 and (short_responses / len(user_lines) > get_settings().metrics_automation_bias_ratio):
            automation_bias = 1.0

    # 2. Say-Do Gap / Illusion of Competence
    # If Reflection exists (Claims) but History is purely mechanical (Do).
    # Heuristic: Reflection has content, but History is dominated by "Execute" commands or short confirmations.
    mechanical_keywords = ["tilaa", "vahvista", "generoi", "ok", "kyllä", "jatka"]
    mechanical_count = 0
    total_words = 0

    for line in user_lines:
        words = line.split()
        total_words += len(words)
        for w in words:
            if any(mk in w for mk in mechanical_keywords):
                mechanical_count += 1

    imperative_command_count = mechanical_count

    if True:
        # If > 50% of user words are mechanical commands, assume Gap.
        if total_words > 0 and (mechanical_count / total_words > get_settings().metrics_mechanical_ratio):
            say_do_gap = 1.0
            illusion_of_competence = 1.0

    return {
        "say_do_gap": say_do_gap,
        "automation_bias": automation_bias,
        "illusion_of_competence": illusion_of_competence,
        "imperative_command_count": imperative_command_count,
    }


@hook_registry.register(name="calculate_control_ratio")
def calculate_control_ratio_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Standalone hook to provide input control ratio if requested explicitly by a DAG step."""
    inputs = state.inputs

    # Dynamically scan all string inputs
    all_text = ""
    if isinstance(inputs, dict):
        all_text = " ".join(str(v) for v in inputs.values() if v)

    ratio = calculate_control_ratio(all_text)
    return HookResult(success=True, state_delta={"input_control_ratio": ratio})


@hook_registry.register(name="calculate_text_metrics")
def text_metrics(state: HookState, deps: HookDependencies) -> HookResult:
    """Calculates text metrics and behavioral heuristics from input data.

    Expects 'inputs' containing 'history_text' and 'product_text'.
    Returns a dictionary with 'audit_metrics' and 'input_control_ratio'.
    """
    logger.debug("[MetricsHook] Running text_metrics hook...")

    # Strict: Inputs MUST exist
    inputs = state.inputs

    if not inputs or not isinstance(inputs, dict):
        error_code = ErrorCodes.INVALID_JSON_PAYLOAD
        msg = f"Missing or invalid 'inputs' in data: {type(inputs)}. Expected dict."
        logger.error("[MetricsHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

    # Dynamically combine ALL string input fields for text metric analysis
    all_text = " ".join(str(v) for v in inputs.values() if v)

    if not all_text.strip():
        logger.warning("[MetricsHook] No valid text found in any input fields.")
        # If absolutely no inputs were provided but they reached here, fail fast.
        error_code = ErrorCodes.EMPTY_INPUT
        msg = "Missing text in inputs for metrics analysis."
        logger.error("[MetricsHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

    try:
        # Calculate Metrics using combined text
        base_metrics = analyze_text(all_text)
        control_ratio = calculate_control_ratio(all_text)
        behavioral_metrics = calculate_behavioral_metrics(base_metrics)

        # Merge results into a single output dict
        audit_metrics = {
            # Text Metrics
            "word_count": base_metrics["word_count"],
            "sentence_count": base_metrics["sentence_count"],
            "avg_sentence_length": base_metrics["avg_sentence_length"],
            "lexical_diversity": base_metrics["lexical_diversity"],
            "capitalization_ratio": base_metrics["capitalization_ratio"],
            "control_ratio": control_ratio,
            # Behavioral Metrics
            "say_do_gap": behavioral_metrics["say_do_gap"],
            "automation_bias": behavioral_metrics["automation_bias"],
            "illusion_of_competence": behavioral_metrics["illusion_of_competence"],
            "imperative_command_count": behavioral_metrics["imperative_command_count"],
        }

        logger.info("[MetricsHook] Metrics calculated successfully.")

        # Return the strictly enforced dict -> dict output
        return HookResult(
            success=True,
            state_delta={
                "profiler_metrics": audit_metrics,
            },
        )

    except Exception as e:
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error("[MetricsHook] %s: %s", error_code.name, e, exc_info=True)
        raise AppException(
            message=f"Failed to calculate metrics: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e
