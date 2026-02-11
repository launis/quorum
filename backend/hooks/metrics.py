"""Metrics hooks for calculating text statistics and control ratios."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.models.state import WorkflowState


from backend.models.domain import TextMetrics

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
            capitalization_ratio=0.0
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



# --- WORKFLOW STATE WRAPPERS (for HOOK_MAPPING compatibility) ---



def calculate_behavioral_metrics(history_text: str, reflection_text: str) -> dict[str, float]:
    """Calculates heuristic behavioral metrics (Say-Do Gap, Automation Bias).
    
    NOTE: These are heuristic approximations to serve as a 'Single Source of Truth' 
    alongside the LLM's qualitative analysis.
    """
    metrics = {
        "say_do_gap": 0.0,
        "automation_bias": 0.0,
        "illusion_of_competence": 0.0
    }
    
    if not history_text:
        return metrics

    # 1. Automation Bias (Heuristic: Short, affirmative user messages)
    # If user messages are consistently short (< 5 words) and frequent.
    user_lines = [line.lower().strip() for line in history_text.split('\n') 
                  if line.lower().startswith(('user:', 'human:', 'k:', 'me:', 'minä:'))]
    
    if user_lines:
        short_responses = sum(1 for line in user_lines if len(line.split()) < 5)
        if len(user_lines) > 2 and (short_responses / len(user_lines) > 0.7):
            metrics["automation_bias"] = 1.0

    # 2. Say-Do Gap / Illusion of Competence
    # If Reflection exists (Claims) but History is purely mechanical (Do).
    # Heuristic: Reflection has content, but History is dominated by "Execute" commands or short confirmations.
    if reflection_text and len(reflection_text) > 50:
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
        if total_words > 0 and (mechanical_count / total_words > 0.5):
            metrics["say_do_gap"] = 1.0
            metrics["illusion_of_competence"] = 1.0

    return metrics


def calculate_text_metrics_hook(state: WorkflowState) -> WorkflowState:
    """WorkflowState wrapper for calculate_text_metrics and behavioral metrics.

    Extracts text from state.context_variables['inputs'], calculates metrics,
    and stores result in state.context_variables['audit_metrics'].
    """
    logger.debug("[MetricsHook] Running calculate_text_metrics_hook...")

    if not state.context_variables:
        return state

    inputs = state.context_variables.get("inputs", {})
    if not isinstance(inputs, dict):
        return state

    # Combine history and product text
    history = inputs.get("history_text", "") or ""
    product = inputs.get("product_text", "") or ""
    reflection = inputs.get("reflection_text", "") or ""
    text = history + "\n" + product

    # Helper to create default metrics
    def create_defaults():
        return TextMetrics(
            word_count=0,
            sentence_count=0,
            avg_sentence_length=0.0,
            lexical_diversity=0.0,
            capitalization_ratio=0.0
        ).model_dump()

    final_metrics = create_defaults()
    
    if text.strip():
        metrics = calculate_text_metrics(text)
        final_metrics = metrics.model_dump()

    # Add Behavioral
    behavioral = calculate_behavioral_metrics(history, reflection)
    final_metrics.update(behavioral)
    
    # Add Control Ratio (Compute it here to ensure it's in the main dictionary for UI)
    control_res = calculate_control_ratio(history)
    final_metrics["control_ratio"] = control_res  # This enables the UI Gauge!
    
    logger.info(f"[MetricsHook] Final Merged Metrics: {final_metrics}")

    # IMMUTABILITY FIX: Update context_variables via model_copy
    new_context = state.context_variables.copy()
    new_context["audit_metrics"] = final_metrics
    new_context["profiler_metrics"] = final_metrics
    
    return state.model_copy(update={"context_variables": new_context})


def calculate_control_ratio_hook(state: WorkflowState) -> WorkflowState:
    """WorkflowState wrapper for calculate_control_ratio.

    Extracts history_text, calculates ratio, stores in state.context_variables['input_control_ratio'].
    """
    logger.debug("[MetricsHook] Running calculate_control_ratio_hook...")

    if not state.context_variables:
        return state

    inputs = state.context_variables.get("inputs", {})
    if not isinstance(inputs, dict):
        return state

    history_text = inputs.get("history_text", "") or ""

    # Return Dict now
    ratio_data = calculate_control_ratio(history_text)
    
    # HEAVY DEBUGGING
    logger.info(f"[MetricsHook] Control Ratio Data: {ratio_data}")
    
    # IMMUTABILITY FIX: Update context_variables via model_copy
    new_context = state.context_variables.copy()
    new_context["input_control_ratio"] = ratio_data
    
    return state.model_copy(update={"context_variables": new_context})
