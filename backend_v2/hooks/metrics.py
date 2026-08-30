"""Metrics hooks for calculating text statistics and control ratios.

All metrics rules adhere strictly to the Phase 9 architecture standards.
"""

import logging
import re
from typing import Any

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.metrics import (
    BehavioralMetricsDTO,
    MetricsPayloadDTO,
    ProfilerMetricsDTO,
    TextMetricsDTO,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


def analyze_text(text: str) -> TextMetricsDTO:
    """Calculates objective text metrics from the input text using simple heuristic counting.

    Metrics include word count, sentence count, avg sentence length, lexical diversity,
    and capitalization ratio.

    Args:
        text: The raw input text.

    Returns:
        Strictly typed metrics payload.
    """
    if not text or not text.strip():
        return TextMetricsDTO(
            word_count=0,
            sentence_count=0,
            avg_sentence_length=0.0,
            lexical_diversity=0.0,
            capitalization_ratio=0.0,
            control_ratio=0.0,
        )

    # 1. Word Count
    words = re.findall(r"\b\w+\b", text.lower())
    word_count = len(words)

    # 2. Sentence Count
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    sentence_count = len(sentences)

    # 3. Averages
    avg_sent_len = word_count / sentence_count if sentence_count > 0 else 0.0

    # 4. Diversity
    unique_words = set(words)
    lex_diversity = len(unique_words) / word_count if word_count > 0 else 0.0

    # 5. Caps
    caps = sum(1 for c in text if c.isupper())
    total_chars = sum(1 for c in text if c.isalpha())
    cap_ratio = caps / total_chars if total_chars > 0 else 0.0

    return TextMetricsDTO(
        word_count=word_count,
        sentence_count=sentence_count,
        avg_sentence_length=round(avg_sent_len, 2),
        lexical_diversity=round(lex_diversity, 2),
        capitalization_ratio=round(cap_ratio, 2),
        control_ratio=0.0,
    )


def calculate_control_ratio(text: str) -> float:
    """Calculates ratio of Human Tokens vs Total Tokens (approximation using characters).

    Formula: UserChars / (UserChars + AIChars)

    Args:
        text: The conversation history or transcript.

    Returns:
        Control ratio between 0.0 (Pure AI) and 1.0 (Pure Human).
    """
    if not text:
        return 0.0

    user_chars = 0
    ai_chars = 0

    lines = text.split("\n")
    current_speaker = "user"

    user_headers = ["user:", "human:", "k:", "k\u00e4ytt\u00e4j\u00e4:", "me:", "min\u00e4:"]
    ai_headers = ["ai:", "assistant:", "t:", "teko\u00e4ly:", "gpt:", "bot:"]

    for line in lines:
        lower_line = line.strip().lower()
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

        if not started_new_block and current_speaker:
            clean_len = len(line.strip())
            match current_speaker:
                case "user":
                    user_chars += clean_len
                case "ai":
                    ai_chars += clean_len
                case _:
                    pass

    total_chars = user_chars + ai_chars
    if total_chars == 0:
        return 0.0

    return round(user_chars / total_chars, 4)


def calculate_behavioral_metrics(text: str, settings: Any) -> BehavioralMetricsDTO:
    """Calculates heuristic behavioral metrics (Say-Do Gap, Automation Bias).

    Args:
        text: The dialogue or document logs.
        settings: Dynamically injected application settings DTO.

    Returns:
        BehavioralMetricsDTO containing the analyzed behavioral patterns.
    """
    say_do_gap = 0.0
    automation_bias = 0.0
    illusion_of_competence = 0.0
    imperative_command_count = 0

    if not text:
        return BehavioralMetricsDTO(
            say_do_gap=say_do_gap,
            automation_bias=automation_bias,
            illusion_of_competence=illusion_of_competence,
            imperative_command_count=imperative_command_count,
        )

    lines = text.split("\n")
    user_lines: list[str] = []

    user_headers = ["user:", "human:", "k:", "k\u00e4ytt\u00e4j\u00e4:", "me:", "min\u00e4:"]
    ai_headers = ["ai:", "assistant:", "t:", "teko\u00e4ly:", "gpt:", "bot:"]
    current_speaker = "user"

    for line in lines:
        lower_line = line.strip().lower()
        started_new = False

        for h in user_headers:
            if lower_line.startswith(h):
                current_speaker = "user"
                content = line[len(h) :].strip()
                if content:
                    user_lines.append(content)
                started_new = True
                break

        if not started_new:
            for h in ai_headers:
                if lower_line.startswith(h):
                    current_speaker = "ai"
                    started_new = True
                    break

        if not started_new and current_speaker == "user" and line.strip():
            user_lines.append(line.strip())

    if user_lines:
        threshold = settings.metrics_short_response_word_count
        short_responses = sum(1 for line in user_lines if len(line.split()) < threshold)

        if len(user_lines) > 2 and (short_responses / len(user_lines) > settings.metrics_automation_bias_ratio):
            automation_bias = 1.0

        mechanical_keywords = ["tilaa", "vahvista", "generoi", "ok", "kyll\u00e4", "jatka"]
        mechanical_count = sum(
            1 for line in user_lines for w in line.split() if any(mk in w.lower() for mk in mechanical_keywords)
        )
        total_words = sum(len(line.split()) for line in user_lines)

        imperative_command_count = mechanical_count

        if total_words > 0 and (mechanical_count / total_words > settings.metrics_mechanical_ratio):
            say_do_gap = 1.0
            illusion_of_competence = 1.0

    return BehavioralMetricsDTO(
        say_do_gap=say_do_gap,
        automation_bias=automation_bias,
        illusion_of_competence=illusion_of_competence,
        imperative_command_count=imperative_command_count,
    )


@hook_registry.register(name="calculate_control_ratio")
def calculate_control_ratio_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Standalone hook to provide input control ratio if requested explicitly by a DAG step.

    Args:
        state: The current execution hook state containing input data.
        deps: The dynamically injected hook dependencies.

    Returns:
        HookResult: Structured execution output.

    Raises:
        AppException: If input validation fails.
    """
    raw_inputs = (
        state.inputs.raw_inputs
        if isinstance(state.inputs, ExecutionInputsDTO)
        else (state.inputs if isinstance(state.inputs, dict) else {})
    )
    try:
        payload = MetricsPayloadDTO.model_validate(raw_inputs)
    except ValidationError as e:
        msg = f"Invalid metrics inputs schema: {e}"
        logger.error("[MetricsHook] %s: %s", ErrorCodes.INVALID_JSON_PAYLOAD.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD.value},
        ) from e

    inputs = payload.root
    all_text = " ".join(str(v) for v in inputs.values() if v)
    ratio = calculate_control_ratio(all_text)
    return HookResult(success=True, state_delta=HookDeltaDTO(delta={"input_control_ratio": ratio}))


@hook_registry.register(name="calculate_text_metrics")
def text_metrics(state: HookState, deps: HookDependencies) -> HookResult:
    """Calculates text metrics and behavioral heuristics from input data.

    Args:
        state: The current execution hook state containing inputs.
        deps: Injected dependencies for environment parameters.

    Returns:
        HookResult: Struct containing resulting calculated metrics state delta.

    Raises:
        AppException: If validation fails or processing encounters an execution error.
    """
    logger.debug("[MetricsHook] Running text_metrics hook...")

    raw_inputs = (
        state.inputs.raw_inputs
        if isinstance(state.inputs, ExecutionInputsDTO)
        else (state.inputs if isinstance(state.inputs, dict) else {})
    )
    try:
        payload = MetricsPayloadDTO.model_validate(raw_inputs)
    except ValidationError as e:
        msg = f"Invalid metrics inputs schema: {e}"
        logger.error("[MetricsHook] %s: %s", ErrorCodes.INVALID_JSON_PAYLOAD.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD.value},
        ) from e

    inputs = payload.root
    all_text = " ".join(str(v) for v in inputs.values() if v)

    user_only = None
    for k, v in inputs.items():
        if k.endswith("_user_only") and isinstance(v, str) and v.strip():
            user_only = v
            break

    text_for_analysis = user_only if user_only else all_text

    if not all_text.strip():
        msg = "Missing text in inputs for metrics analysis."
        logger.error("[MetricsHook] %s: %s", ErrorCodes.EMPTY_INPUT.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.EMPTY_INPUT.value},
        )

    try:
        base_metrics = analyze_text(text_for_analysis)
        control_ratio = calculate_control_ratio(all_text)

        settings = get_settings()
        behavioral_metrics = calculate_behavioral_metrics(all_text, settings)

        audit_metrics = ProfilerMetricsDTO(
            word_count=base_metrics.word_count,
            sentence_count=base_metrics.sentence_count,
            avg_sentence_length=base_metrics.avg_sentence_length,
            lexical_diversity=base_metrics.lexical_diversity,
            capitalization_ratio=base_metrics.capitalization_ratio,
            control_ratio=control_ratio,
            say_do_gap=behavioral_metrics.say_do_gap,
            automation_bias=behavioral_metrics.automation_bias,
            illusion_of_competence=behavioral_metrics.illusion_of_competence,
            imperative_command_count=behavioral_metrics.imperative_command_count,
        )

        logger.info("[MetricsHook] Metrics calculated successfully.")

        return HookResult(
            success=True,
            state_delta=HookDeltaDTO(
                delta={
                    "profiler_metrics": audit_metrics.model_dump(mode="json"),
                }
            ),
        )

    except Exception as e:
        logger.error("[MetricsHook] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, e, exc_info=True)
        raise AppException(
            message=f"Failed to calculate metrics: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
