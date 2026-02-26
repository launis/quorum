"""Metrics hooks for calculating text statistics and control ratios."""

from __future__ import annotations

import logging
import re

from backend.exceptions import AppException, ErrorCodes
from backend.models.domain.inputs import WorkflowInputs
from backend.models.domain.profiler import BehavioralMetrics, ProfilerMetrics, TextMetrics
from backend.models.state import WorkflowState
from backend.settings import get_settings

logger = logging.getLogger(__name__)


def calculate_text_metrics(text: str) -> TextMetrics:
    """Calculates objective text metrics from the input text using simple heuristic counting.

    Metrics include word count, sentence count, avg sentence length, lexical diversity,
    and capitalization ratio.

    Args:
        text (str): The raw input text.

    Returns:
        TextMetrics: Key metrics object.

    """
    if not text or not text.strip():
        return TextMetrics(
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
    avg_sent_len = word_count / sentence_count if sentence_count > 0 else 0

    # 4. Diversity
    unique_words = set(words)
    lex_diversity = len(unique_words) / word_count if word_count > 0 else 0

    # 5. Caps
    caps = sum(1 for c in text if c.isupper())
    total_chars = sum(1 for c in text if c.isalpha())
    cap_ratio = caps / total_chars if total_chars > 0 else 0

    return TextMetrics(
        word_count=word_count,
        sentence_count=sentence_count,
        avg_sentence_length=round(avg_sent_len, 2),
        lexical_diversity=round(lex_diversity, 2),
        capitalization_ratio=round(cap_ratio, 2),
        control_ratio=0.0,  # Default, calculated separately in hook or explicit call
    )


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
    current_speaker = None  # 'user' or 'ai'

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


def calculate_behavioral_metrics(history_text: str, reflection_text: str) -> BehavioralMetrics:
    """Calculates heuristic behavioral metrics (Say-Do Gap, Automation Bias).

    NOTE: These are heuristic approximations to serve as a 'Single Source of Truth'
    alongside the LLM's qualitative analysis.
    """
    say_do_gap = 0.0
    automation_bias = 0.0
    illusion_of_competence = 0.0

    if not history_text:
        return BehavioralMetrics()

    # 1. Automation Bias (Heuristic: Short, affirmative user messages)
    # If user messages are consistently short (< 5 words) and frequent.
    user_lines = [
        line.lower().strip()
        for line in history_text.split("\n")
        if line.lower().startswith(("user:", "human:", "k:", "me:", "minä:"))
    ]

    if user_lines:
        short_responses = sum(
            1 for line in user_lines if len(line.split()) < get_settings().metrics_short_response_word_count
        )
        if len(user_lines) > 2 and (short_responses / len(user_lines) > get_settings().metrics_automation_bias_ratio):
            automation_bias = 1.0

    # 2. Say-Do Gap / Illusion of Competence
    # If Reflection exists (Claims) but History is purely mechanical (Do).
    # Heuristic: Reflection has content, but History is dominated by "Execute" commands or short confirmations.
    if reflection_text and len(reflection_text) > get_settings().metrics_reflection_min_length:
        # Check if history is "rich" or "mechanical"
        # Mechanical keywords
        mechanical_keywords = ["tilaa", "vahvista", "generoi", "ok", "kyllä", "jatka"]
        mechanical_count = 0
        total_words = 0

        for line in user_lines:
            words = line.split()
            total_words += len(words)
            for w in words:
                if any(mk in w for mk in mechanical_keywords):
                    mechanical_count += 1

        # If > 50% of user words are mechanical commands, assume Gap.
        if total_words > 0 and (mechanical_count / total_words > get_settings().metrics_mechanical_ratio):
            say_do_gap = 1.0
            illusion_of_competence = 1.0

    return BehavioralMetrics(
        say_do_gap=say_do_gap, automation_bias=automation_bias, illusion_of_competence=illusion_of_competence
    )


def calculate_text_metrics_hook(state: WorkflowState) -> WorkflowState:
    """WorkflowState wrapper for calculate_text_metrics and behavioral metrics.

    Extracts text from state.context_variables['inputs'], calculates metrics,
    and stores result in state.context_variables['audit_metrics'].

    Unified hook: Also calculates and sets 'input_control_ratio'.
    """
    logger.debug("[MetricsHook] Running calculate_text_metrics_hook...")

    # Strict Enforce: State must be WorkflowState object
    if isinstance(state, dict):
        raise AppException(
            message="Metrics Hook received dict state. Strict Pydantic Enforcement Violation.",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    if not state.context_variables:
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        msg = "No context_variables found."
        raise AppException(message=msg, status_code=500, details={"error_code": error_code})

    # Strict: Inputs MUST be WorkflowInputs (or inflatable to it)
    inputs_data = state.context_variables.get("inputs")  # Keep for null check
    inputs = state.get_context("inputs", WorkflowInputs)

    if not inputs:
        # Fail Fast: Inputs are mandatory for metrics
        # Distinguish between Missing and Invalid
        if inputs_data is None:
            error_code = ErrorCodes.EMPTY_INPUT
            msg = "Missing 'inputs' in context_variables."
            # Logic fix for 500 error: If inputs are missing, it's a BAD REQUEST (400) not Internal Error
            status_code = 400
        else:
            error_code = ErrorCodes.INVALID_JSON_PAYLOAD
            msg = f"Invalid 'inputs' data: {type(inputs_data)}. Expected WorkflowInputs."
            status_code = 500

        logger.error(f"[MetricsHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=status_code, details={"error_code": error_code})

    # Combine history and product text
    history = inputs.history_text or ""
    product = inputs.product_text or ""
    reflection = inputs.reflection_text or ""
    text = f"{history}\n{product}"

    if not text.strip():
        # Fail Fast (Part 18.1): If no text to analyze, this is likely an error in a text processing pipeline.
        pass

    # STRICT INPUT CHECK
    if not inputs.history_text and not inputs.product_text:
        error_code = ErrorCodes.EMPTY_INPUT
        msg = "Missing 'history_text' or 'product_text' in inputs."
        logger.error(f"[MetricsHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=400, details={"error_code": error_code})

    try:
        # 1. Text Metrics
        metrics_model = calculate_text_metrics(text)

        # 2. Control Ratio
        control_res = calculate_control_ratio(history)

        # Update control ratio in the model (create new instance since frozen)
        metrics_model = metrics_model.model_copy(update={"control_ratio": control_res})

        # 3. Behavioral Metrics
        behavioral_model = calculate_behavioral_metrics(history, reflection)

        # 4. Construct Structured Model
        combined_dict = {
            **metrics_model.model_dump(),
            **behavioral_model.model_dump()
        }
        profiler_metrics = ProfilerMetrics(**combined_dict)

        # IMMUTABILITY FIX: Update context_variables via model_copy
        new_context = state.context_variables.copy()

        # We store the Pydantic model directly
        new_context["audit_metrics"] = profiler_metrics
        new_context["profiler_metrics"] = profiler_metrics

        # Unified: Set standalone control ratio to deprecate separate hook requirement
        new_context["input_control_ratio"] = control_res

        logger.info(f"[MetricsHook] Final Merged Metrics: {profiler_metrics.model_dump()}")

        return state.model_copy(update={"context_variables": new_context})

    except Exception as e:
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error(f"[MetricsHook] {error_code.name}: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to calculate metrics: {e}", status_code=500, details={"error_code": error_code}
        ) from e
