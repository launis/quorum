"""Metrics hooks for calculating text statistics and control ratios."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def calculate_text_metrics(text: str) -> dict[str, Any]:
    """Calculates objective text metrics from the input text using simple heuristic counting.

    Metrics include word count, sentence count, avg sentence length, lexical diversity,
    and capitalization ratio.

    Args:
        text (str): The raw input text.

    Returns:
        Dict[str, Any]: Key metrics (e.g. {'word_count': 150, 'lexical_diversity': 0.45}).

    """
    if not text or not text.strip():
        return {}

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

def calculate_text_metrics_hook(state) -> "WorkflowState":
    """WorkflowState wrapper for calculate_text_metrics.
    
    Extracts text from state.inputs, calculates metrics, and stores in aux_data.
    """
    from backend.models.state import WorkflowState
    
    logger.info("[MetricsHook] Running calculate_text_metrics_hook...")
    
    if not hasattr(state, "inputs") or not state.inputs:
        return state
    
    # Combine history and product text
    history = getattr(state.inputs, "history_text", "") or ""
    product = getattr(state.inputs, "product_text", "") or ""
    text = history + "\n" + product
    
    if not text.strip():
        logger.warning("[MetricsHook] No text to analyze.")
        return state
    
    metrics = calculate_text_metrics(text)
    state.aux_data["profiler_metrics"] = metrics
    logger.info(f"[MetricsHook] Metrics calculated: {metrics}")
    
    return state


def calculate_control_ratio_hook(state) -> "WorkflowState":
    """WorkflowState wrapper for calculate_control_ratio.
    
    Extracts history_text from state.inputs, calculates ratio, and stores in aux_data.
    """
    from backend.models.state import WorkflowState
    
    logger.info("[MetricsHook] Running calculate_control_ratio_hook...")
    
    if not hasattr(state, "inputs") or not state.inputs:
        return state
    
    history_text = getattr(state.inputs, "history_text", "") or ""
    
    if not history_text.strip():
        logger.warning("[MetricsHook] No history text to analyze.")
        return state
    
    ratio = calculate_control_ratio(history_text)
    state.aux_data["input_control_ratio"] = ratio
    logger.info(f"[MetricsHook] Control ratio calculated: {ratio:.4f}")
    
    return state
